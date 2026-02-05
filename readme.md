# PyXooHub

A modular **operating hub** for the Divoom Pixoo 64, built in Python.
This project will turn the Pixoo into a smart dashboard.

## Getting started

* Python 3.10+
* A Divoom Pixoo 64 on the same Wi-Fi network

### Installation

1. Clone the repo.
2. Create a `.env` file with `PIXOO_IP=192.168.x.x`.
3. Run `pip install -r requirements.txt`.
4. Run `python app.py`.

## Roadmap & To-Do List

### Phase 1: Core Engine [COMPLETE]

* [x] Basic Project Structure
* [x] Logging system (console + file)
* [x] Create robust connection function
* [x] Fonts: A generic font system

### Phase 2: The UI engine [IN PROGRESS]

* [x] Base {Widget} class
* [x] **Resources**: Add resources.py where we can store fonts centrally
* [x] **TextWidget**: A simple widget for static labels
* [x] **MediumFont**: Add a medium sized (7 high?) font.
* [ ] **ImageWidget**: Support for drawing icons
* [ ] **Container**: A widget that holds other widgets (for centering/grouping)

### Phase 3: Data Layer (Inplementing Data and API's)

* [ ] **Update Interval**: Modify widgets to have a 'update()' method seperate from 'draw()'
