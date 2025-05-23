import pytest
from dash.testing.application_runners import import_app
from selenium.webdriver.common.by import By
import time  # For debugging pause, if needed


# Fixture to provide the Dash app instance to the tests
@pytest.fixture
def dash_app():
    # Assumes your Dash app is in 'app.py' and the app object is named 'app'
    # If your app object has a different name, e.g., my_dash_app = dash.Dash(...),
    # you would use:
    # from app import my_dash_app
    # app_instance = my_dash_app
    # return app_instance
    app_instance = import_app("app")
    return app_instance


def test_header_exists(dash_duo, dash_app):
    """
    Tests if the header with the correct H1 text is present.
    """
    dash_duo.start_server(dash_app)

    # Wait for the H1 element within the .app-header div
    dash_duo.wait_for_element_by_css_selector(".app-header h1", timeout=5)
    header_h1 = dash_duo.find_element(".app-header h1")
    assert header_h1.text == "Soul Foods: Pink Morsel Sales Visualiser", \
        "Header text is incorrect or H1 not found"


def test_visualization_present(dash_duo, dash_app):
    """
    Tests if the sales line chart (dcc.Graph component) and its content are present.
    """
    dash_duo.start_server(dash_app)

    # Wait for the dcc.Graph component by its ID
    dash_duo.wait_for_element_by_id("sales-line-chart", timeout=10)

    # Verify that the Plotly chart content (SVG) is rendered within the graph component
    dash_duo.wait_for_element_by_css_selector("#sales-line-chart svg.main-svg", timeout=10)

    # As a final check, find the .plotly div
    graph_plotly_div = dash_duo.find_element("#sales-line-chart .plotly")
    assert graph_plotly_div is not None, "Plotly graph's internal .plotly div not found"


def test_region_picker_present(dash_duo, dash_app):
    """
    Tests if the region radio button picker is present and functional.
    """
    dash_duo.start_server(dash_app)

    # Wait for the dcc.RadioItems component container by its ID
    dash_duo.wait_for_element_by_id("region-radio", timeout=7)  # Slightly longer timeout
    radio_items_container = dash_duo.find_element("#region-radio")

    # Wait for at least one radio input to be rendered inside the container
    dash_duo.wait_for_element_by_css_selector("#region-radio input[type='radio']", timeout=7)

    options = radio_items_container.find_elements(By.CSS_SELECTOR, "input[type='radio']")
    # In your app.py, regions is initialized with 'all' and then extended.
    # So, there should be at least 1, but typically 5 (all + 4 cardinal directions)
    # if data loads correctly and regions are found.
    assert len(options) >= 1, f"Expected at least 1 region option, found {len(options)}"
    # If you are sure about the number of regions, you can be more specific:
    # assert len(options) == 5, f"Expected 5 region options, found {len(options)}"

    # Check for the "Select Region:" label
    # This depends on the className you gave it in app.py
    label_for_picker = dash_duo.find_element(".radio-items-label")
    assert "Select Region:" in label_for_picker.text, "Region picker label not found or incorrect"

    # --- DEBUGGING PAUSE ---
    # print(">>> PAUSING FOR 30 SECONDS - INSPECT THE BROWSER NOW <<<")
    # print(">>> Check the HTML for #region-radio input[type='radio'][value='all'] <<<")
    # time.sleep(30) # Uncomment this line to pause and inspect
    # import pdb; pdb.set_trace() # Or uncomment this for a Python debugger breakpoint

    # Wait specifically for the 'all' radio button to be present with its value attribute
    # This selector is quite specific and should work if the HTML is as expected.
    dash_duo.wait_for_element_by_css_selector(
        "#region-radio input[type='radio'][value='all']", timeout=10
    )
    all_option_input = dash_duo.find_element("#region-radio input[type='radio'][value='all']")

    assert all_option_input.is_displayed(), "'All' radio button input is not displayed"
    assert all_option_input.is_enabled(), "'All' radio button input is not enabled"

    # Use JavaScript execution to reliably check the 'checked' property
    is_all_selected = dash_duo.driver.execute_script(
        "return arguments[0].checked;", all_option_input
    )
    assert is_all_selected, "'All' option should be selected by default"

    # --- Test interaction with another radio button ---
    # Find the label associated with the 'west' radio button
    # Dash usually renders <label><input type="radio" value="west">West</label>
    # So we find the label that contains the input with value 'west'

    # First, ensure the 'west' radio input itself is present
    dash_duo.wait_for_element_by_css_selector("#region-radio input[type='radio'][value='west']", timeout=5)

    # Find all labels within the radio items container
    all_labels_in_radio_group = radio_items_container.find_elements(By.CSS_SELECTOR, "label")
    west_label_element = None
    for lbl in all_labels_in_radio_group:
        try:
            # Check if this label contains an input element with value 'west'
            # This is a common structure for dcc.RadioItems where the input is inside the label
            lbl.find_element(By.CSS_SELECTOR, "input[type='radio'][value='west']")
            # If the above line doesn't raise NoSuchElementException, this label is for 'west'
            west_label_element = lbl
            break
        except:  # selenium.common.exceptions.NoSuchElementException
            # This label doesn't contain the 'west' input, continue to the next label
            pass

    assert west_label_element is not None, "Could not find a clickable label for 'West' option"

    # Click the label associated with the 'west' option
    # Ensure it's interactable before clicking
    dash_duo.wait_for_element_by_css_selector(
        f"#{west_label_element.get_attribute('for')}" if west_label_element.get_attribute(
            'for') else "label:has(input[value='west'])",
        timeout=5
    )  # This selector is a bit complex, might need adjusting based on actual HTML
    west_label_element.click()

    # Verify 'West' is now selected
    dash_duo.wait_for_element_by_css_selector("#region-radio input[type='radio'][value='west']:checked", timeout=5)
    west_option_input_after_click = dash_duo.find_element("#region-radio input[type='radio'][value='west']")
    is_west_selected = dash_duo.driver.execute_script(
        "return arguments[0].checked;", west_option_input_after_click
    )
    assert is_west_selected, "'West' option was not selected after click"

    # Optional: Check if the graph title updates as expected
    # This requires knowing the exact text and selector for the graph title
    # Example:
    # dash_duo.wait_for_text_to_equal("YOUR_GRAPH_TITLE_SELECTOR", "Pink Morsel Sales - Region: West", timeout=5)