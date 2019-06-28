require 'nokogiri'
require 'open-uri'
require 'pry-byebug'
require 'json'

PAGE_URL = ARGV[0] || 'http://store.united-arrows.co.jp/shop/uasons/goods.html?gid=9700472'

def get_table_by_wrapper_div(html, class_name)
  html.css("div.#{class_name} table")
end

def get_table_headers(table)
  table.css("tr").first.css("th.dtl").collect { |header| header.text }
end

def get_table_body(table)
  table.css("tr").drop(1)
end

def get_cell_data(row)
  row.css("td").collect { |cell| cell.text }
end

def get_product_id(page)
  table = get_table_by_wrapper_div(page, "detail")
  get_cell_data(get_table_body(table).last).last
end

def get_product_name(page)
  page.css("div.item_detail div.ttl p.item").text
end

def get_sizes(page)
  table = get_table_by_wrapper_div(page, "size")
  tbody = get_table_body(table)
  headers = get_table_headers(table)

  sizes = Hash.new
  tbody.each do |row|
    cells = get_cell_data(row)
    each_size = Hash.new
    # This could be done more elegantly with the dictionary comprehension in Python :)
    cells.drop(1).each_with_index { |cell, index| each_size["#{headers[index]}"] = cell.to_f }
    sizes["#{cells.shift}"] = each_size
  end
  sizes
end

def build_output_hash(page)
  { id: get_product_id(page) }
    .merge({ name: get_product_name(page) })
    .merge({ sizes: get_sizes(page) })
end

def main
  begin
    page = Nokogiri::HTML.parse(open(PAGE_URL, "r:Shift_JIS").read)
  rescue Exception => e
    puts "Couldn't parse #{PAGE_URL}: #{e}"
    exit
  end
  JSON.pretty_generate(build_output_hash(page))
end

puts main
