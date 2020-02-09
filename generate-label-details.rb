#!/usr/bin/env ruby

require "json"
require "pry-byebug"

BANK_SIZE = Integer("4000", 16)

ROM_FILE = ENV.fetch("ROM_FILE", "./crystal-speedchoice.gbc")
ROM_FILE_BASENAME = File.basename(ROM_FILE, File.extname(ROM_FILE))
SYM_FILE = "#{ROM_FILE_BASENAME}.sym"
OUT_FILE = "#{ROM_FILE_BASENAME}-label-details.json"

# there's no ASM-level label for this, so we have to handle it
# specially.
ILEX_FOREST_TREE = 721295

def rom
  @rom ||= IO.binread(ROM_FILE)
end

def byte_to_string(byte)
  "$#{byte.ord.to_s(16)}"
end

def label_hex_addresses
  File
    .read(SYM_FILE)
    .split("\n")
    .select { |l| l.include?("ckir") }
    .map { |line| line.split(" ") }
    .map { |address, label| [label, address] }
end

def label_addresses
  @label_addresses ||= Hash[label_hex_addresses.map do |label, hex_address|
    bank, internal_address = hex_address.split(":").map { |val| Integer(val, 16) }
    address = (internal_address % BANK_SIZE) + (bank * BANK_SIZE)
    [label, address]
  end]
end

def rom_bytes_to_integers(rom_bytes)
  rom_bytes.split('').map(&:bytes).flatten.join(" ")
end

def ilex_forest_diff
  {
    "integer_values" => rom_bytes_to_integers(rom[ILEX_FOREST_TREE]),
    "address_range" => {
      "begin" => ILEX_FOREST_TREE,
      "end" => ILEX_FOREST_TREE + 1,
    },
    "label" => "Remove cuttable tree in Ilex Forest",
  }
end

def main
  label_address_ranges =
    label_addresses
      .keys
      .reject { |label| label.include?("ckir_AFTER") }
      .map do |label|
        post_label = label.gsub("ckir_BEFORE", "ckir_AFTER")
        puts(label)
        puts(label_addresses[label])
        puts(post_label)
        puts(label_addresses[post_label])
        puts(label_addresses[label]...label_addresses[post_label])
        address_range = label_addresses[label]...label_addresses[post_label]
        [label, address_range]
      end

  label_details =
    label_address_ranges.map do |label, address_range|
      {
        "label" => label,
        "address_range" => { "begin" => address_range.begin, "end" => address_range.end },
        "integer_values" => rom_bytes_to_integers(rom[address_range]),
        "hex_values" => rom[address_range].each_char.map(&method(:byte_to_string)).join(" "),
      }
  end.sort_by { |details| details["label"] }

  label_details << ilex_forest_diff

  File.write(OUT_FILE, label_details.to_json)

  STDERR.puts "generated #{OUT_FILE}"
end

main