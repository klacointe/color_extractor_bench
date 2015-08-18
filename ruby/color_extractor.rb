require 'optparse'
require 'kolors'
require 'color'
require 'rmagick'
require 'yaml'
include Magick

options = {}
OptionParser.new do |opts|
  opts.banner = 'Usage: color_extractor.rb [options]'

  opts.on('-i PATH', '--image PATH', 'Image to analyze') do |i|
    options[:image] = i
  end

  opts.on('-o PATH', '--output PATH', 'Image to generate') do |o|
    options[:output] = o
  end

  opts.on('-p PATH', '--palette PATH', 'Yaml colors path') do |o|
    options[:colors] = o
  end

  opts.on('-h', '--help', 'Prints this help') do
    puts opts
    exit
  end
end.parse!

kolors = Kolors::DominantColors.new options[:image]

Kolors.options[:image_magick_path] = '/usr/bin/convert'
Kolors.options[:resolution] = '100x100'
#Kolors.options[:color_count] = 5

width = 800
height = 600
color_width = 200
color_height = 60

if options[:colors]
  KEY_COLORS = YAML.load_file(options[:colors]).inject({}) do |h, (hex, name)|
    rgb = Color::RGB.from_html(hex)
    h[Kolors::Rgb.new(rgb.red, rgb.green, rgb.blue).to_lab] = name
    h
  end
end

f = Image.new(width, height) do
  self.background_color = "white"
end
i = Magick::Image.read(options[:image]) {self.size = "100x100"}.first
i.resize_to_fit! width - color_width, height
f.composite! i, NorthWestGravity, OverCompositeOp

kolors.color_bins_result.each_with_index do |color, i|
  color_name = color.keys.first
  percent = color.values.first
  lab = KEY_COLORS.key color_name
  rgb = Kolors::Lab.new(*lab).to_rgb
  hex = Color::RGB.new(*rgb).html
  c = Image.new(color_width, color_height) do
    self.background_color = "rgb(#{rgb[0]},#{rgb[1]},#{rgb[2]})"
  end
  text = Draw.new
  text.annotate(c, 0, 0, 0, 0, "#{color_name} - #{hex} - #{percent.round}%") do
    text.gravity = CenterGravity
    self.pointsize = 10
    self.font_family = "Arial"
    self.font_weight = BoldWeight
    self.stroke = "none"
  end
  f.composite! c, width - color_width, color_height * i , OverCompositeOp
end

f.write(options[:output])
