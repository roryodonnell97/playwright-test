import asyncio
import re
from playwright.async_api import Playwright, async_playwright


# Function for selecting seats. Tracks seat selected count, waits for count to increase before selecting a new seat. 
# Had issues with seats not being selected properly without this check
async def click_seat_and_wait(page, index: int):
    # Count selected seats before click
    selected_seat_count = await page.locator("div.seatmap__seat-text").count()

    # Click desired seat button
    await page.locator("button.ng-star-inserted").nth(index).click()

    # Wait until a new seat gets selected
    await page.wait_for_function(
        f'document.querySelectorAll("div.seatmap__seat-text").length > {selected_seat_count}'
    )
    

# Main function
async def run(playwright: Playwright) -> None:
    
    # Launch Firefox browser
    print("-----START-----")
    print("\nStage 1 - Go to https://www.ryanair.com/")
    print(" -> Launch browser")
    browser = await playwright.firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    # Navigate to Ryanair website
    print(" -> Navigate to Ryanair website")
    response = await page.goto("https://www.ryanair.com/ie/en")

    # If option for cookies shows, decline
    print(" -> Decline cookies if necessary")
    if await page.get_by_role("button", name="No, thanks").is_visible():
        await page.get_by_role("button", name="No, thanks").click()

    # Stage 1 Assertions
    print("\nAssertions")

    # Assert response code is 200
    assert response.status == 200, f"Expected status 200, but got {response.status}"
    print(f"    Passed - HTTP status code is {response.status} (OK)")

    # Assert page title is correct
    title = await page.title()
    assert "Ryanair" in title, f"Ryanair, but got '{title}'"
    print(f"    Passed - Page title is correct: '{title}'")
    

    # Choose departure and destination locations
    print("\nStage 2 - Serach for a flight")
    print(" -> Choose departure and destination locations")
    await page.get_by_role("textbox", name="From").click()
    await page.get_by_role("button", name="Ireland").click()
    await page.get_by_role("button", name="Dublin").click()
    await page.get_by_role("button", name="Spain").click()
    await page.get_by_role("button", name="Madrid").click()

    # Choose flight dates, select 3rd month available & 2nd + 5th day available (3 night stay)
    print(" -> Choose flight dates")
    await page.locator("div.m-toggle__month").nth(2).click()
    await page.locator("div.calendar-body__cell").nth(1).click()
    await page.locator("div.calendar-body__cell").nth(4).click()

    # Increase number of passengers to 2 adults
    print(" -> Increase number of passengers to 2 adults")
    await page.get_by_role("button", name="Passengers 1 Adult").click()
    await page.locator(".counter__button-wrapper--enabled").first.click()
    await page.get_by_role("button", name="Done").click()

    # Assertions
    print("\nAssertions")
    # Assert From location is correct
    from_input = page.get_by_role("textbox", name="From")
    from_value = await from_input.input_value()
    assert "Dublin" in from_value, f"Expected 'Dublin' in input, but got '{from_value}'"
    print(f"    Passed - From textbox contains: '{from_value}'")

    # Assert To location is correct
    to_input = page.get_by_role("textbox", name="To")
    to_value = await to_input.input_value()
    assert "Madrid" in to_value, f"Expected 'Madrid' in input, but got '{to_value}'"
    print(f"    Passed - To textbox contains: '{to_value}'")

    # Assert depart date has a value
    depart_button = page.get_by_role("button", name=re.compile(r"Depart.*"))
    depart_text = await depart_button.inner_text()
    assert re.search(r"\d{1,2} \w{3}", depart_text), f"Depart button text does not contain a date: '{depart_text}'"
    print(f"    Passed - Depart button has a date: '{depart_text}'")

    # Assert return date has a value
    return_button = page.get_by_role("button", name=re.compile(r"Return.*"))
    return_text = await return_button.inner_text()
    assert re.search(r"\d{1,2} \w{3}", return_text), f"Return button text does not contain a date: '{return_text}'"
    print(f"    Passed - Return button has a date: '{return_text}'")

    # Assert there are 2 adult passengers
    passengers_button = page.get_by_role("button", name="Passengers 2 Adult")
    passengers_text = await passengers_button.inner_text()
    assert "2 Adult" in passengers_text, f"Expected '2 Adult' in button, but got '{passengers_text}'"
    print(f"    Passed: Passengers button contains: '{passengers_text}'")

    # Click "Search" button, navigate to new page
    print("\n -> Click 'Search' button, navigate to new page")
    async with page.expect_navigation():
        await page.get_by_role("button", name="Search").click()


    # Select first option available for both flights
    print("\nStage 3 - Select suggested flights")
    print(" -> Select first option available for both flights")
    await page.locator(".flight-card__bumper").first.click()
    await page.locator("div").filter(has_text=re.compile(r"^Ryanair$")).first.click()
    await page.locator(".fare-table__fare-column-border.fare-table__fare-column-border--regu").click()

    # Select option to log in later
    print("\nStage 4 - Choose 'Log in later'")
    print(" -> Select option to log in later")
    await page.get_by_role("button", name="Log in later").click()

    print("\nStage 5 - Enter any valid values in fields in “Passengers” section and click [Continue]")
    # Add details for 1st passenger, Mr. John Doe
    print(" -> Add details for 1st passenger, Mr. John Doe")
    await page.locator("pax-passenger").filter(has_text="Passenger 1 Adult Title -").get_by_role("button").click()
    await page.get_by_role("button", name="Mr", exact=True).click()
    await page.locator("input[name=\"form.passengers.ADT-0.name\"]").click()
    await page.locator("input[name=\"form.passengers.ADT-0.name\"]").fill("John")
    await page.locator("[id=\"form.passengers.ADT-0.surname\"]").click()
    await page.locator("[id=\"form.passengers.ADT-0.surname\"]").fill("Doe")

    # Add details for 2nd passenger, Ms. Jane Roe
    print(" -> Add details for 2nd passenger, Ms. Jane Roe")
    await page.get_by_role("button", name="-").click()
    await page.get_by_role("button", name="Ms").click()
    await page.locator("input[name=\"form.passengers.ADT-1.name\"]").click()
    await page.locator("input[name=\"form.passengers.ADT-1.name\"]").fill("Jane")
    await page.locator("[id=\"form.passengers.ADT-1.surname\"]").click()
    await page.locator("[id=\"form.passengers.ADT-1.surname\"]").fill("Roe")

    # Assertions
    print("\nAssertions")
    # Assert 1st passenger names are correct
    passenger1_name_input = page.locator('input[name="form.passengers.ADT-0.name"]')
    passenger1_surname_input = page.locator("[id=\"form.passengers.ADT-0.surname\"]")
    passenger1_name_value = await passenger1_name_input.input_value()
    passenger1_surname_value = await passenger1_surname_input.input_value()
    assert "John" in passenger1_name_value, f"Expected 'John' in input, but got '{passenger1_name_value}'"
    assert "Doe" in passenger1_surname_value, f"Expected 'Doe' in input, but got '{passenger1_surname_value}'"
    print(f"    Passed - Passenger 1 name input contains: '{passenger1_name_value}'")
    print(f"    Passed - Passenger 1 surname input contains: '{passenger1_surname_value}'")

    # Assert 2nd passenger names are correct
    passenger2_name_input = page.locator('input[name="form.passengers.ADT-1.name"]')
    passenger2_surname_input = page.locator("[id=\"form.passengers.ADT-1.surname\"]")
    passenger2_name_value = await passenger2_name_input.input_value()
    passenger2_surname_value = await passenger2_surname_input.input_value()
    assert "Jane" in passenger2_name_value, f"Expected 'Jane' in input, but got '{passenger2_name_value}'"
    assert "Roe" in passenger2_surname_value, f"Expected 'Roe' in input, but got '{passenger2_surname_value}'"
    print(f"    Passed - Passenger 2 name input contains: '{passenger2_name_value}'")
    print(f"    Passed - Passenger 2 surname input contains: '{passenger2_surname_value}'")

    # Click "Continue" buttom, navigate to new page
    print(" -> Click 'Continue' button, navigate to new page")
    async with page.expect_navigation():
        await page.get_by_role("button", name="Continue").click()

    # For outgoing flight, select 1st and 2nd seats available
    print("\nStage 6 - Choose any available seats and click [Next]")
    print(" -> For outgoing flight, select 1st and 2nd seats available")
    await click_seat_and_wait(page, 0)
    await click_seat_and_wait(page, 1)
    
    # Click "Next flight" button, allow next flight to load by checking the "MAD - DUB" element contains  "--active" 
    print(" -> Click 'Next flight' button and allow next flight to load")
    await page.get_by_role("button", name="Next flight").click()
    await page.wait_for_selector(".passenger-carousel__orig-dest--active:text('MAD - DUB')", state="visible")

    # For return flight, select 2nd and 3rd seats available
    print("\nStage 7 - Choose any available seats and click [Continue]")
    print(" -> For return flight, select 2nd and 3rd seats available")
    await click_seat_and_wait(page, 2)
    await click_seat_and_wait(page, 3)

    # Click "Continue" button
    print(" -> Click 'Continue' button")
    await page.get_by_role("button", name="Continue").click()

    # Click "No, thanks" button for Fast Track option, navigate to new page
    print(" -> Click 'No, thanks' button for Fast Track option, navigate to new page")
    async with page.expect_navigation():
        await page.get_by_role("button", name="No, thanks").click()

    # Wait for page to load fully by checking "Cabin Bags" element to be visible
    print(" -> Wait for page to load fully")
    await page.wait_for_selector("span:text('Cabin Bags')", state="visible")
    
    # Close context and browser
    print(" -> Close browser")
    await context.close()
    await browser.close()
    print("\n-----END-----")



async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())