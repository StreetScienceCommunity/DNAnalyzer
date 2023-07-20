### Script adapted from Galaxy Training Network script
### https://github.com/galaxyproject/training-material/

#!/usr/bin/env ruby
require 'yaml'
require 'shellwords'
require 'json'

fn = ARGV[0]
fn_metadata = File.join(File.dirname(fn) , 'metadata.md')
metadata = YAML.load_file(fn_metadata)

ARI_MAP = File.expand_path(File.join(__dir__, 'ari-map.yml'))
WORD_MAP = {}
YAML.load_file(ARI_MAP).each_pair do |k,v|
 WORD_MAP.merge!({k.downcase => v})
end

APPROVED_VOICES = {
  "en" => [
    {"id" =>"Amy"     , "lang" => "en-GB" , "neural" => true},
    {"id" =>"Aria"    , "lang" => "en-NZ" , "neural" => true},
    {"id" =>"Brian"   , "lang" => "en-GB" , "neural" => true},
    {"id" =>"Emma"    , "lang" => "en-GB" , "neural" => true},
    {"id" =>"Joanna"  , "lang" => "en-US" , "neural" => true},
    {"id" =>"Joey"    , "lang" => "en-US" , "neural" => true},
    {"id" =>"Kendra"  , "lang" => "en-US" , "neural" => true},
    {"id" =>"Matthew" , "lang" => "en-US" , "neural" => true},
    {"id" =>"Nicole"  , "lang" => "en-AU" , "neural" => false},
    {"id" =>"Olivia"  , "lang" => "en-AU" , "neural" => true},
    {"id" =>"Raveena" , "lang" => "en-IN" , "neural" => false},
    {"id" =>"Salli"   , "lang" => "en-US" , "neural" => true}
  ],
  "es" => [
    { "id" => "Miguel"   , "lang" => "es-US" , "neural" => false },
    { "id" => "Mia"      , "lang" => "es-MX" , "neural" => false },
    { "id" => "Enrique"  , "lang" => "es-ES" , "neural" => false },
    { "id" => "Conchita" , "lang" => "es-ES" , "neural" => false },
    { "id" => "Lupe"     , "lang" => "es-US" , "neural" => true }
  ]
}

m_lang = metadata.fetch('lang', 'en')
m_voice = metadata.fetch('voice', nil)

# Parse the material for the slide notes
file = File.open(fn)
lines = file.readlines.map(&:chomp)

# The structure will be
# ---
# meta
# ---
#
# contents

# +1 because we skipped the 0th entry, +1 again to not include the `---`
# end_meta = lines[1..-1].index("---") + 1

# Strip off the metadata
contents = lines

# This will be our final script
blocks = [[metadata['title']]]


# Accumulate portions between ??? and ---
current_block = []
in_notes = false
contents.each{ |x|
  # Check whether we're in the notes or out of them.
  if x == "???" then
    in_notes = true
  elsif x == "---" or x == "--" then
    if in_notes then
      blocks.push(current_block)
      current_block = []
    end

    in_notes = false
  end

  if in_notes then
    current_block.push(x)
  end
}
blocks.push(current_block)

if m_lang == "en" then
  blocks.push(["Thank you for watching!"])
elsif m_lang == "es" then
  blocks.push(["¡Gracias por ver este vídeo!"])
else
  blocks.push(["Thank you for watching!"])
end

# For each block, cleanup first.
blocks = blocks.map{ |block|
  # Remove the - prefix from each line
  script_lines = block.map{ |x| x.strip.delete_prefix("- ") }
  # Remove the leading ???
  if script_lines[0] == '???'
    script_lines = script_lines[1..-1]
  end
  # Remove blank entries
  script_lines = script_lines.select{ |x| x.length != 0 }
  script_lines = script_lines.map{ |line|
    line.delete_prefix("- ")
    line.gsub!(/`/, '"')
    # If they don't end with punctuation, fix it.
    if ! (line.end_with?('.') or line.end_with?('?') or line.end_with?('!'))
      line += '.'
    end

    line
  }
  script_lines
}

#out_subs.write(blocks.map{ |line| line.join(" ") }.join("\n"))
res = Hash.new
res["blocks"] = blocks

if m_voice.nil? then
  if m_lang == "en" then
    res["voice"] = APPROVED_VOICES['en'].sample
  elsif m_lang == "es" then
    res["voice"] = APPROVED_VOICES['es'].sample
  else
    res["voice"] = APPROVED_VOICES['en'].sample
  end
else
  res["voice"] = metadata['voice']
end

print JSON.pretty_generate(res)
