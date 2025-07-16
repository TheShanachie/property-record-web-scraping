# TODO List

## General
- [ ] Verify error handling strategies. The current strategy is a mess.
- [ ] Review and fix outdated function doc strings.
- [ ] Make sure that docstrings are up to date
- [ ] Validate packages, being used
- [ ] Document authors and LLM usage.

## Error Handling 
- [ ] When relevant, verify that each method properly handles errors

#### E.H. in ScraperUtils.Driver
- [x] Driver.Driver.init
- [x] Driver.Driver.apply
- [x] Driver.Driver.pass_disclaimer
- [x] Driver.Driver.address_search

#### E.H. in ScraperUtils.GetElement
- [x] GetElement.expect_web_element
- [x] GetElement.expect_web_elements
- [x] GetElement.check_web_element
- [x] GetElement.wait_for_page
- [x] GetElement.wait_for_subpage
- [x] GetElement.click_element

#### E.H. in ScraperUtils.PhotoScraper
- [x] PhotoScraper.enode_image_to_base64
- [x] PhotoScraper.decode_base64_to_image
- [x] PhotoScraper.scrape_current_photo
- [x] PhotoScraper.scrape_photo_page

#### E.H. in ScraperUtils.RecordScraper
- [ ] Record.parse_record_card
- [ ] Record.parse_record_tables
- [ ] Record.go_to_record_page
- [ ] Record.is_table_card_arrow
- [ ] Record.next_record
- [ ] Record.press_table_card_arrow
- [ ] Record.parse_record
- [ ] Record.get_record_heading
- [ ] Record.get_listing_index

##### E.H. in ScraperUtils.RecordSearch
- [ ] Record.submit_address_search