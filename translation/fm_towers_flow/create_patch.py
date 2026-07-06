import os

def main():
    flow_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(flow_dir))
    
    patches_dir = os.path.join(base_dir, "patches")
    os.makedirs(patches_dir, exist_ok=True)
    
    patch_path = os.path.join(patches_dir, "scummvm_loom_voice.patch")
    
    patch_content = """diff --git a/engines/scumm/actor.cpp b/engines/scumm/actor.cpp
index 7c48e492..41d2249f 100644
--- a/engines/scumm/actor.cpp
+++ b/engines/scumm/actor.cpp
@@ -3528,6 +3528,11 @@ void ScummEngine::actorTalk(const byte *msg) {
 	_charsetBufPos = 0;
 	_talkDelay = 0;
 	_haveMsg = 0xFF;
 	VAR(VAR_HAVE_MSG) = 0xFF;
 	if (VAR_CHARCOUNT != 0xFF)
 		VAR(VAR_CHARCOUNT) = 0;
 	_haveActorSpeechMsg = true;
+	// CHT non-talkie TTS dub: play a synthesised Chinese voice for this line (if a
+	// matching voice/<hash>.ext exists). Plays on the talk channel so the existing
+	// "hold subtitle while talk sound runs" logic syncs the subtitle duration.
+	if (_useCJKMode && (_language == Common::ZH_CHN || _language == Common::ZH_TWN) && _sound)
+		_sound->playChtVoice(_charsetBuffer, getTalkingActor());
 #ifdef USE_TTS
 	stopTextToSpeech();
 #endif
diff --git a/engines/scumm/string.cpp b/engines/scumm/string.cpp
index ebb998ec..511bd5a6 100644
--- a/engines/scumm/string.cpp
+++ b/engines/scumm/string.cpp
@@ -109,6 +109,11 @@ void ScummEngine::printString(int m, const byte *msg) {
 	case 1:
+		if (_useCJKMode && (_language == Common::ZH_CHN || _language == Common::ZH_TWN) && _sound && _currentRoom != 1) {
+			byte buf[2048];
+			convertMessageToString(msg, buf, sizeof(buf));
+			_sound->playChtVoice(buf, 0xFF);
+		}
 #ifdef USE_TTS
 		_voiceNextString = true;
 #endif
 		drawString(1, msg);
 		break;
diff --git a/engines/scumm/sound.h b/engines/scumm/sound.h
index 2b9b1e66..7e425118 100644
--- a/engines/scumm/sound.h
+++ b/engines/scumm/sound.h
@@ -120,6 +120,8 @@ public:
 	Sound(ScummEngine *parent, Audio::Mixer *mixer, bool useReplacementAudioTracks);
 	~Sound() override;
 	virtual void startSound(int sound, int heOffset = 0, int heChannel = 0, int heFlags = 0, int heFreq = 0, int hePan = 0, int heVol = 0);
+	// CHT non-talkie TTS dub: play voice/<hash>.<ext> for a displayed CJK line on the talk channel.
+	void playChtVoice(const byte *buf, int actor);
 	virtual void addSoundToQueue(int sound, int heOffset = 0, int heChannel = 0, int heFlags = 0, int heFreq = 0, int hePan = 0, int heVol = 0);
 	void processSound();
diff --git a/engines/scumm/sound.cpp b/engines/scumm/sound.cpp
index bfb33823..478ebc96 100644
--- a/engines/scumm/sound.cpp
+++ b/engines/scumm/sound.cpp
@@ -23,6 +23,7 @@
 #include "common/util.h"
 #include "common/ptr.h"
 #include "common/substream.h"
+#include "common/memstream.h"
  
 #include "scumm/actor.h"
@@ -120,6 +121,110 @@ void Sound::startSound(int sound, int offset, int channel, int flags, int freq,
 void Sound::startSound(int sound, int offset, int channel, int flags, int freq, int pan, int volume) {
 	if (_vm->VAR_LAST_SOUND != 0xFF)
 		_vm->VAR(_vm->VAR_LAST_SOUND) = sound;
 	_lastSound = sound;
  
 	addSoundToQueue(sound, offset, channel, flags, freq, pan, volume);
 }
+
+// Wraps an AudioStream but reports a different sample rate, so the mixer resamples it
+// faster/slower -> a cheap per-actor pitch+pace nudge for the shared NPC voice.
+namespace {
+class ChtRateShiftStream : public Audio::AudioStream {
+	Audio::AudioStream *_p;
+	int _rate;
+public:
+	ChtRateShiftStream(Audio::AudioStream *p, int rate) : _p(p), _rate(rate) {}
+	~ChtRateShiftStream() override { delete _p; }
+	int readBuffer(int16 *b, int n) override { return _p->readBuffer(b, n); }
+	bool isStereo() const override { return _p->isStereo(); }
+	int getRate() const override { return _rate; }
+	bool endOfData() const override { return _p->endOfData(); }
+};
+} // namespace
+
+// CHT non-talkie TTS dub. Play game-dir voice/<key>.<ext> on the talk channel with
+// kTalkSoundID so the engine's existing "hold text while talk sound runs" logic
+// syncs the subtitle display duration.
+void Sound::playChtVoice(const byte *buf, int actor) {
+	if (!buf || !*buf)
+		return;
+
+	// FNV-1a 32-bit hash on all bytes except control codes (0xFF...) and whitespace (<= 0x20)
+	uint32 h = 2166136261u;
+	int n = 0;
+	for (const byte *p = buf; *p; ) {
+		if (p[0] == 0xFF) {
+			if (p[1] == 1 || p[1] == 2 || p[1] == 3 || p[1] == 8) {
+				p += 2;
+			} else if (p[1] == 9 || p[1] == 10 || p[1] == 12 || p[1] == 13 || p[1] == 14) {
+				p += 4;
+			} else {
+				p += 2;
+			}
+		} else if (p[0] <= 0x20) {
+			p++;
+		} else {
+			h = (h ^ p[0]) * 16777619u;
+			p++;
+			n++;
+		}
+	}
+	if (n == 0)
+		return; // no valid characters -> nothing to play
+
+	debug(3, "LOOM CHTMAP actor %d key %08x", actor, (unsigned)h);
+
+	ScummFile f(_vm);
+	bool opened = false;
+	int extIdx = -1;
+	const char *exts[] = { ".wav", ".ogg", ".voc" };
+	Common::String name;
+
+	// 1. Try voice/a<actor>/<key>.<ext>
+	for (int i = 0; i < 3 && !opened; i++) {
+		name = Common::String::format("voice/a%d/%08x%s", actor, (unsigned)h, exts[i]);
+		opened = _vm->openFile(f, Common::Path(name));
+		if (opened) extIdx = i;
+	}
+
+	// 2. Try voice/npc/<key>.<ext> if it's an NPC
+	int ego = (_vm->VAR_EGO != 0xFF) ? _vm->VAR(_vm->VAR_EGO) : -1;
+	bool isNpc = (actor != ego && actor > 0 && actor < 0x80);
+	if (!opened && isNpc) {
+		for (int i = 0; i < 3 && !opened; i++) {
+			name = Common::String::format("voice/npc/%08x%s", (unsigned)h, exts[i]);
+			opened = _vm->openFile(f, Common::Path(name));
+			if (opened) extIdx = i;
+		}
+	}
+
+	// 3. Try voice/<key>.<ext>
+	if (!opened) {
+		for (int i = 0; i < 3 && !opened; i++) {
+			name = Common::String::format("voice/%08x%s", (unsigned)h, exts[i]);
+			opened = _vm->openFile(f, Common::Path(name));
+			if (opened) extIdx = i;
+		}
+	}
+
+	if (!opened)
+		return;
+
+	uint32 sz = (uint32)f.size();
+	if (!sz || sz > 16 * 1024 * 1024)
+		return;
+
+	byte *data = (byte *)malloc(sz);
+	if (!data)
+		return;
+	f.read(data, sz);
+
+	Common::MemoryReadStream *ms = new Common::MemoryReadStream(data, sz, DisposeAfterUse::YES);
+	Audio::SeekableAudioStream *stream = nullptr;
+
+	if (extIdx == 0) {
+		stream = Audio::makeWAVStream(ms, DisposeAfterUse::YES);
+	} else if (extIdx == 1) {
#ifdef USE_VORBIS
+		stream = Audio::makeVorbisStream(ms, DisposeAfterUse::YES);
#endif
+	} else if (extIdx == 2) {
+		stream = Audio::makeVOCStream(ms, Audio::FLAG_UNSIGNED, DisposeAfterUse::YES);
+	}
+
+	if (!stream)
+		return;
+
+	Audio::AudioStream *out = stream;
+	// Per-NPC pitch variation when using shared voice/npc/
+	if (actor != ego && actor > 0 && actor < 0x80 && name.contains("voice/npc/")) {
+		int base = stream->getRate();
+		int off = (int)(((actor * 2654435761u) >> 28) % 13) - 6; // -6..+6
+		out = new ChtRateShiftStream(stream, base + base * off / 100);
+	}
+
+	_mixer->stopID(kTalkSoundID);
+	_mixer->playStream(Audio::Mixer::kSpeechSoundType, _talkChannelHandle, out, kTalkSoundID);
}"""
    patch_content = patch_content.replace("\\t", "\t")
    with open(patch_path, 'w', newline='\n', encoding='utf-8') as f:
        f.write(patch_content)
    print(f"Generated ScummVM patch file at {patch_path}")

if __name__ == "__main__":
    main()