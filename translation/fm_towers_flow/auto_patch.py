import os
import difflib

def generate_diff(orig_path, mod_content, repo_rel_path):
    with open(orig_path, 'r', encoding='utf-8', errors='ignore') as f:
        orig_lines = f.readlines()
    
    # splitlines(keepends=True) ensures that we keep the newlines on all lines
    mod_lines = mod_content.splitlines(keepends=True)
    
    # We use lineterm='\n' so that header lines have newlines
    diff = list(difflib.unified_diff(
        orig_lines, 
        mod_lines, 
        fromfile=f"a/{repo_rel_path}", 
        tofile=f"b/{repo_rel_path}", 
        lineterm='\n'
    ))
    return "".join(diff)

def main():
    scummvm_dir = r"D:\git\scummvm"
    loom_dir = r"D:\git\遊戲中文化\LOOM"
    
    # 1. actor.cpp
    actor_path = os.path.join(scummvm_dir, "engines", "scumm", "actor.cpp")
    with open(actor_path, 'r', encoding='utf-8', errors='ignore') as f:
        actor_orig = f.read()
    
    # Target insertion point
    target_str = "\t_haveActorSpeechMsg = true;"
    insert_str = "\n\t// CHT non-talkie TTS dub: play a synthesised Chinese voice for this line (if a\n\t// matching voice/<hash>.ext exists). Plays on the talk channel so the existing\n\t// \"hold subtitle while talk sound runs\" logic syncs the subtitle duration.\n\tif (_useCJKMode && _sound)\n\t\t_sound->playChtVoice(_charsetBuffer, getTalkingActor());"
    
    if target_str not in actor_orig:
        print("Error: Target string not found in actor.cpp")
        return
        
    actor_mod = actor_orig.replace(target_str, target_str + insert_str, 1)
    diff_actor = generate_diff(actor_path, actor_mod, "engines/scumm/actor.cpp")
    
    # 2. string.cpp
    string_path = os.path.join(scummvm_dir, "engines", "scumm", "string.cpp")
    with open(string_path, 'r', encoding='utf-8', errors='ignore') as f:
        string_orig = f.read()
        
    target_str = "\tcase 1:"
    insert_str = "\n\t\tif (_useCJKMode && _sound && _currentRoom != 1) {\n\t\t\tbyte buf[2048];\n\t\t\tconvertMessageToString(msg, buf, sizeof(buf));\n\t\t\t_sound->playChtVoice(buf, 0xFF);\n\t\t}"
    
    if target_str not in string_orig:
        print("Error: Target string not found in string.cpp")
        return
        
    string_mod = string_orig.replace(target_str, target_str + insert_str, 1)
    diff_string = generate_diff(string_path, string_mod, "engines/scumm/string.cpp")
    
    # 3. sound.h
    sound_h_path = os.path.join(scummvm_dir, "engines", "scumm", "sound.h")
    with open(sound_h_path, 'r', encoding='utf-8', errors='ignore') as f:
        sound_h_orig = f.read()
        
    target_str = "\tvirtual void startSound(int sound, int heOffset = 0, int heChannel = 0, int heFlags = 0, int heFreq = 0, int hePan = 0, int heVol = 0);"
    insert_str = "\n\t// CHT non-talkie TTS dub: play voice/<hash>.<ext> for a displayed CJK line on the talk channel.\n\tvoid playChtVoice(const byte *buf, int actor);"
    
    if target_str not in sound_h_orig:
        print("Error: Target string not found in sound.h")
        return
        
    sound_h_mod = sound_h_orig.replace(target_str, target_str + insert_str, 1)
    diff_sound_h = generate_diff(sound_h_path, sound_h_mod, "engines/scumm/sound.h")
    
    # 4. sound.cpp
    sound_cpp_path = os.path.join(scummvm_dir, "engines", "scumm", "sound.cpp")
    with open(sound_cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
        sound_cpp_orig = f.read()
        
    # Include insertion
    target_inc = '#include "common/substream.h"'
    insert_inc = '\n#include "common/memstream.h"\n#include "audio/decoders/wave.h"\n#include "audio/decoders/vorbis.h"\n#include "audio/decoders/voc.h"'
    if target_inc not in sound_cpp_orig:
        print("Error: Target include not found in sound.cpp")
        return
        
    sound_cpp_mod1 = sound_cpp_orig.replace(target_inc, target_inc + insert_inc, 1)
    
    # Function definition insertion
    target_func = """void Sound::startSound(int sound, int offset, int channel, int flags, int freq, int pan, int volume) {
	if (_vm->VAR_LAST_SOUND != 0xFF)
		_vm->VAR(_vm->VAR_LAST_SOUND) = sound;
	_lastSound = sound;

	addSoundToQueue(sound, offset, channel, flags, freq, pan, volume);
}"""
    
    insert_func = """

// Wraps an AudioStream but reports a different sample rate, so the mixer resamples it
// faster/slower -> a cheap per-actor pitch+pace nudge for the shared NPC voice.
namespace {
class ChtRateShiftStream : public Audio::AudioStream {
	Audio::AudioStream *_p;
	int _rate;
public:
	ChtRateShiftStream(Audio::AudioStream *p, int rate) : _p(p), _rate(rate) {}
	~ChtRateShiftStream() override { delete _p; }
	int readBuffer(int16 *b, int n) override { return _p->readBuffer(b, n); }
	bool isStereo() const override { return _p->isStereo(); }
	int getRate() const override { return _rate; }
	bool endOfData() const override { return _p->endOfData(); }
};
} // namespace

// CHT non-talkie TTS dub. Play game-dir voice/<key>.<ext> on the talk channel with
// kTalkSoundID so the engine's existing "hold text while talk sound runs" logic
// syncs the subtitle display duration.
void Sound::playChtVoice(const byte *buf, int actor) {
	if (!buf || !*buf)
		return;

	// FNV-1a 32-bit hash on all bytes except control codes (0xFF...) and whitespace (<= 0x20)
	uint32 h = 2166136261u;
	int n = 0;
	for (const byte *p = buf; *p; ) {
		if (p[0] == 0xFF) {
			if (p[1] == 1 || p[1] == 2 || p[1] == 3 || p[1] == 8) {
				p += 2;
			} else if (p[1] == 9 || p[1] == 10 || p[1] == 12 || p[1] == 13 || p[1] == 14) {
				p += 4;
			} else {
				p += 2;
			}
		} else if (p[0] <= 0x20) {
			p++;
		} else {
			h = (h ^ p[0]) * 16777619u;
			p++;
			n++;
		}
	}
	if (n == 0)
		return; // no valid characters -> nothing to play

	debug(3, "LOOM CHTMAP actor %d key %08x", actor, (unsigned)h);

	ScummFile f(_vm);
	bool opened = false;
	int extIdx = -1;
	const char *exts[] = { ".wav", ".ogg", ".voc" };
	Common::String name;

	// 1. Try voice/a<actor>/<key>.<ext>
	for (int i = 0; i < 3 && !opened; i++) {
		name = Common::String::format("voice/a%d/%08x%s", actor, (unsigned)h, exts[i]);
		opened = _vm->openFile(f, Common::Path(name));
		if (opened) extIdx = i;
	}

	// 2. Try voice/npc/<key>.<ext> if it's an NPC
	int ego = (_vm->VAR_EGO != 0xFF) ? _vm->VAR(_vm->VAR_EGO) : -1;
	bool isNpc = (actor != ego && actor > 0 && actor < 0x80);
	if (!opened && isNpc) {
		for (int i = 0; i < 3 && !opened; i++) {
			name = Common::String::format("voice/npc/%08x%s", (unsigned)h, exts[i]);
			opened = _vm->openFile(f, Common::Path(name));
			if (opened) extIdx = i;
		}
	}

	// 3. Try voice/<key>.<ext>
	if (!opened) {
		for (int i = 0; i < 3 && !opened; i++) {
			name = Common::String::format("voice/%08x%s", (unsigned)h, exts[i]);
			opened = _vm->openFile(f, Common::Path(name));
			if (opened) extIdx = i;
		}
	}

	if (!opened)
		return;

	uint32 sz = (uint32)f.size();
	if (!sz || sz > 16 * 1024 * 1024)
		return;

	byte *data = (byte *)malloc(sz);
	if (!data)
		return;
	f.read(data, sz);

	Common::MemoryReadStream *ms = new Common::MemoryReadStream(data, sz, DisposeAfterUse::YES);
	Audio::SeekableAudioStream *stream = nullptr;

	if (extIdx == 0) {
		stream = Audio::makeWAVStream(ms, DisposeAfterUse::YES);
	} else if (extIdx == 1) {
#ifdef USE_VORBIS
		stream = Audio::makeVorbisStream(ms, DisposeAfterUse::YES);
#endif
	} else if (extIdx == 2) {
		stream = Audio::makeVOCStream(ms, Audio::FLAG_UNSIGNED, DisposeAfterUse::YES);
	}

	if (!stream)
		return;

	Audio::AudioStream *out = stream;
	// Per-NPC pitch variation when using shared voice/npc/
	if (actor != ego && actor > 0 && actor < 0x80 && name.contains("voice/npc/")) {
		int base = stream->getRate();
		int off = (int)(((actor * 2654435761u) >> 28) % 13) - 6; // -6..+6
		out = new ChtRateShiftStream(stream, base + base * off / 100);
	}

	_mixer->stopID(kTalkSoundID);
	_mixer->playStream(Audio::Mixer::kSpeechSoundType, _talkChannelHandle, out, kTalkSoundID);
}"""
    
    # We must normalize newlines to make sure the target string matches
    target_func_norm = target_func.replace('\r\n', '\n')
    sound_cpp_mod1_norm = sound_cpp_mod1.replace('\r\n', '\n')
    
    if target_func_norm not in sound_cpp_mod1_norm:
        print("Error: Target startSound implementation not found in sound.cpp")
        # Let's try with different whitespace
        target_func_norm_alt = target_func_norm.replace('\t', '    ')
        sound_cpp_mod1_norm_alt = sound_cpp_mod1_norm.replace('\t', '    ')
        if target_func_norm_alt in sound_cpp_mod1_norm_alt:
            print("Found with spaces instead of tabs! Normalizing.")
            sound_cpp_mod1_norm = sound_cpp_mod1_norm_alt.replace(target_func_norm_alt, target_func_norm_alt + insert_func.replace('\t', '    '), 1)
        else:
            return
    else:
        sound_cpp_mod1_norm = sound_cpp_mod1_norm.replace(target_func_norm, target_func_norm + insert_func, 1)
        
    diff_sound_cpp = generate_diff(sound_cpp_path, sound_cpp_mod1_norm, "engines/scumm/sound.cpp")
    
    # 5. charset.cpp (Typography adjustments for line spacing and character spacing)
    charset_path = os.path.join(scummvm_dir, "engines", "scumm", "charset.cpp")
    with open(charset_path, 'r', encoding='utf-8', errors='ignore') as f:
        charset_orig = f.read()
        
    # Line spacing (行距): Change return _vm->_useCJKMode ? 8 : _fontHeight; to 9 (adds 2px gap)
    target_str_line = "\treturn _vm->_useCJKMode ? 8 : _fontHeight;"
    insert_str_line = "\treturn _vm->_useCJKMode ? 9 : _fontHeight;"
    
    # Character spacing (字距): Change spacing = 8; to spacing = 9; (adds 2px gap)
    target_str_char = """\tif (_vm->_useCJKMode) {
		if (chr >= 256)
			spacing = 8;
		else if (chr >= 128)
			spacing = 4;
	}"""
    insert_str_char = """\tif (_vm->_useCJKMode) {
		if (chr >= 256)
			spacing = 9;
		else if (chr >= 128)
			spacing = 4;
	}"""
    
    charset_mod = charset_orig
    if target_str_line in charset_mod:
        charset_mod = charset_mod.replace(target_str_line, insert_str_line, 1)
    else:
        print("Error: Target line spacing string not found in charset.cpp")
        
    if target_str_char in charset_mod:
        charset_mod = charset_mod.replace(target_str_char, insert_str_char, 1)
    else:
        print("Error: Target char spacing string not found in charset.cpp")
        
    diff_charset = generate_diff(charset_path, charset_mod, "engines/scumm/charset.cpp")
    
    # 6. scumm.cpp (Hold subtitle text on screen while TTS voice is playing)
    scumm_path = os.path.join(scummvm_dir, "engines", "scumm", "scumm.cpp")
    with open(scumm_path, 'r', encoding='utf-8', errors='ignore') as f:
        scumm_orig = f.read()
        
    target_str_scumm = "\t_talkDelay -= delta;\n\tif (_talkDelay < 0)\n\t\t_talkDelay = 0;"
    insert_str_scumm = """\t_talkDelay -= delta;
\t
\t// CHT non-talkie TTS dub: hold subtitle on screen while TTS voice is still playing
\tif (_useCJKMode && _haveActorSpeechMsg && _sound && _sound->_talkChannelHandle && _mixer->isSoundHandleActive(*_sound->_talkChannelHandle)) {
\t\tif (_talkDelay < 1)
\t\t\t_talkDelay = 1;
\t} else if (_talkDelay < 0) {
\t\t_talkDelay = 0;
\t}"""
    
    scumm_mod = scumm_orig
    # Normalize newlines for search
    scumm_orig_norm = scumm_orig.replace('\r\n', '\n')
    target_str_scumm_norm = target_str_scumm.replace('\r\n', '\n')
    
    if target_str_scumm_norm in scumm_orig_norm:
        scumm_mod = scumm_orig_norm.replace(target_str_scumm_norm, insert_str_scumm, 1)
    else:
        print("Error: Target _talkDelay string not found in scumm.cpp")
        
    diff_scumm = generate_diff(scumm_path, scumm_mod, "engines/scumm/scumm.cpp")
    
    # Concatenate all diffs
    full_patch = diff_actor + diff_string + diff_sound_h + diff_sound_cpp + diff_charset + diff_scumm
    
    # Write to target patch file
    patch_dest = os.path.join(loom_dir, "patches", "scummvm_loom_voice.patch")
    with open(patch_dest, 'w', newline='\n', encoding='utf-8') as f:
        f.write(full_patch)
        
    print(f"Generated unified diff patch successfully at {patch_dest}")

if __name__ == '__main__':
    main()
