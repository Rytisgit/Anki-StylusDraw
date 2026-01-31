# -*- coding: utf-8 -*-
# Copyright: Michal Krassowski <krassowski.michal@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""
Initially based on the Anki-TouchScreen addon, updated ui and added pressure pen/stylus capabilities, perfect freehand(line smoothing) and calligrapher functionality.


It adds an AnkiDraw menu entity with options like:

    switching AnkiDraw
    modifying some of the colors
    thickness
    toolbar settings


If you want to contribute visit GitHub page: https://github.com/Rytisgit/Anki-StylusDraw
Also, feel free to send me bug reports or feature requests.

Copyright: Michal Krassowski <krassowski.michal@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html,
Important parts of Javascript code inspired by http://creativejs.com/tutorials/painting-with-pixels/index.html
"""

__addon_name__ = "AnkiDraw"
__version__ = "1.7"

from pathlib import Path

from aqt import mw
from aqt.utils import showWarning

from anki.lang import _
from anki.hooks import addHook

from aqt.qt import QAction, QMenu, QColorDialog, QMessageBox, QInputDialog, QLabel,\
   QPushButton, QDialog, QVBoxLayout, QComboBox, QHBoxLayout, QSpinBox, QCheckBox, QFontDialog, QFont
from aqt.qt import QKeySequence,QColor
from aqt.qt import pyqtSlot as slot

# Load extra JS libraries from external files to simplify the __init__.py
file = Path(__file__)
with open(file.with_name("Caligrapher.js"), encoding="utf8") as f:
    caligrapher_js = f.read()
with open(file.with_name("PerfectFreehand.js"), encoding="utf8") as f:
    perfect_freehand_js = f.read()
# This declarations are there only to be sure that in case of troubles
# with "profileLoaded" hook everything will work.

ts_profile_loaded = False

saved_value_defaults = {
    'ts_state_on': True,
    'ts_opacity': 0.8,
    'ts_auto_hide': True,
    'ts_auto_hide_pointer': True,
    'ts_default_small_canvas': False,
    'ts_zen_mode': False,
    'ts_follow': False,
    'ts_pressure_sensitivity': True,
    'ts_orient_vertical': True,
    'ts_y_offset': 2,
    'ts_small_width': 500,
    'ts_small_height': 500,
    'ts_background_color': "#FFFFFF00",
    'ts_x_offset': 2,
    'ts_location': 1,
    'ts_pen1_color': "#272828",
    'ts_pen2_color': "#149beb",
    'ts_pen3_color': "#ced51a",
    'ts_pen4_color': "#da13a8",
    'ts_pen1_width': 4,
    'ts_pen2_width': 6,
    'ts_pen3_width': 20,
    'ts_pen4_width': 8,
    'ts_pen1_opacity': 0.8,
    'ts_pen2_opacity': 0.9,
    'ts_pen3_opacity': 0.5,
    'ts_pen4_opacity': 0.7,
    'ts_font_family': "Arial",
    'ts_font_size': 20,
    'ts_font_bold': False,
    'ts_font_italic': False,
}

# Create the variables in the global scope
for key, value in saved_value_defaults.items():
    globals()[key] = value

ts_default_review_html = mw.reviewer.revHtml
ts_default_VISIBILITY = "true"
ts_default_PerfFreehand = "false"
ts_default_Calligraphy = "false"

def ts_save():
    """
    Saves configurable variables into profile, so they can
    be used to restore previous state after Anki restart.
    """
    # Save all default variables to profile
    for key, value in globals().items():
        if key in saved_value_defaults:
            mw.pm.profile[key] = value

def ts_load():
    """
    Load configuration from profile, set states of checkable menu objects
    and turn on night mode if it were enabled on previous session.
    """
    global ts_profile_loaded
    
    # Load each variable from profile or use default
    for key, default in saved_value_defaults.items():
        globals()[key] = mw.pm.profile.get(key, default)

    ts_profile_loaded = True
    ts_menu_auto_hide.setChecked(ts_auto_hide)
    ts_menu_auto_hide_pointer.setChecked(ts_auto_hide_pointer)
    ts_menu_small_default.setChecked(ts_default_small_canvas)
    ts_menu_zen_mode.setChecked(ts_zen_mode)
    ts_menu_follow.setChecked(ts_follow)
    ts_menu_pressure.setChecked(ts_pressure_sensitivity)
    if ts_state_on:
        ts_on()

    assure_plugged_in()

def execute_js(code):
    web_object = mw.reviewer.web
    web_object.eval(code)

def assure_plugged_in():
    global ts_default_review_html
    if not mw.reviewer.revHtml == custom:
        ts_default_review_html = mw.reviewer.revHtml
        mw.reviewer.revHtml = custom

def resize_js():
    execute_js("if (typeof resize === 'function') { setTimeout(resize, 101); }");
    
def clear_blackboard():
    assure_plugged_in()

    if ts_state_on:
        execute_js("if (typeof clear_canvas === 'function') { clear_canvas(); }")
        # is qFade the reason for having to wait?
        execute_js("if (typeof resize === 'function') { setTimeout(resize, 101); }");

def blackboard_html():
    return u"""
<div id="canvas_wrapper">
    <textarea id="AnkiDrawTextBox" style="width: 0;height: 0;opacity: 0;"></textarea>
    <canvas id="secondary_canvas" width="100" height="100" ></canvas>
    <canvas id="main_canvas" width="100" height="100"></canvas>
    
    <div id="pencil_button_bar">
        <!-- SVG icons from https://github.com/tabler/tabler-icons/ -->
        <button id="ts_visibility_button" class="active" title="Toggle visiblity (, comma)"
              onclick="switch_visibility();" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M4 20h4l10.5 -10.5a1.5 1.5 0 0 0 -4 -4l-10.5 10.5v4"></path><path d="M13.5 6.5l4 4"></path></svg>
        </button>

        <button id="ts_perfect_freehand_button" title="Perfect Freehand (Alt + x)"
              onclick="switch_perfect_freehand()" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M8 20l10.5 -10.5a2.828 2.828 0 1 0 -4 -4l-10.5 10.5v4h4z"></path><path d="M13.5 6.5l4 4"></path><path d="M16 18h4m-2 -2v4"></path></svg>
        </button>

        <button id="ts_kanji_button" title="Toggle calligrapher (Alt + c)"
              onclick="switch_calligraphy_mode();" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M3 21v-4a4 4 0 1 1 4 4h-4"></path><path d="M21 3a16 16 0 0 0 -12.8 10.2"></path><path d="M21 3a16 16 0 0 1 -10.2 12.8"></path><path d="M10.6 9a9 9 0 0 1 4.4 4.4"></path></svg>
        </button>

        <button id="ts_text_button" title="Toggle text writing (Alt + t)"
              onclick="switch_text_writing_mode();" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M19 10h-14" />  <path d="M5 6h14" />  <path d="M14 14h-9" />  <path d="M5 18h6" />  <path d="M18 15v6" />  <path d="M15 18h6" /></svg>        </button>

        <button id="ts_stroke_delete_button" title="Stroke Delete (Alt + d), hold shift+d"
            onclick="switch_stroke_delete_mode()" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M3 3l18 18" /><path d="M19 20h-10.5l-4.21 -4.3a1 1 0 0 1 0 -1.41l5 -4.993m2.009 -2.01l3 -3a1 1 0 0 1 1.41 0l5 5a1 1 0 0 1 0 1.41c-1.417 1.431 -2.406 2.432 -2.97 3m-2.02 2.043l-4.211 4.256" /><path d="M18 13.3l-6.3 -6.3" /></svg>
        </button>
        
        <button id="ts_undo_button" title="Undo the last stroke (Alt + z)"
              onclick="ts_undo();" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M4.05 11a8 8 0 1 1 .5 4m-.5 5v-5h5"></path></svg>
        </button>
        <button id="ts_redo_button" title="Redo the last stroke (Alt + y)"
              onclick="ts_redo();" >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M19.95 11a8 8 0 1 0 -.5 4m.5 5v-5h-5"></path></svg>
        </button>
        <button class="active" title="Clean canvas (. dot)"
              onclick="add_clear_marker();" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M4 7h16"></path><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2l1 -12"></path><path d="M9 7v-3a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v3"></path><path d="M10 12l4 4m0 -4l-4 4"></path></svg>

        <button id="ts_switch_fullscreen_button" class="active" title="Toggle fullscreen canvas(Alt + b)"
              onclick="switch_small_canvas();" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M9.00002 3.99998H4.00004L4 9M20 8.99999V4L15 3.99997M15 20H20L20 15M4 15L4 20L9.00002 20"></path></svg>
        </button>

        <button id="ts_switch_pen1_button" class="active" title="Switch to Pen 1 (Alt + 1)"
              onclick="activate_pen1();" >
        <svg stroke="currentColor" fill="none" stroke-width="1.8" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M18.333 2c1.96 0 3.56 1.537 3.662 3.472l.005 .195v12.666c0 1.96 -1.537 3.56 -3.472 3.662l-.195 .005h-12.666a3.667 3.667 0 0 1 -3.662 -3.472l-.005 -.195v-12.666c0 -1.96 1.537 -3.56 3.472 -3.662l.195 -.005h12.666zm-5.339 5.886c-.083 -.777 -1.008 -1.16 -1.617 -.67l-.084 .077l-2 2l-.083 .094a1 1 0 0 0 0 1.226l.083 .094l.094 .083a1 1 0 0 0 1.226 0l.094 -.083l.293 -.293v5.586l.007 .117a1 1 0 0 0 1.986 0l.007 -.117v-8l-.006 -.114z" /></svg>
        </button>

        <button id="ts_switch_pen2_button" class="active" title="Switch to Pen 2 (Alt + 2)"
              onclick="activate_pen2();" >
        <svg stroke="currentColor" fill="none" stroke-width="1.8" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M18.333 2c1.96 0 3.56 1.537 3.662 3.472l.005 .195v12.666c0 1.96 -1.537 3.56 -3.472 3.662l-.195 .005h-12.666a3.667 3.667 0 0 1 -3.662 -3.472l-.005 -.195v-12.666c0 -1.96 1.537 -3.56 3.472 -3.662l.195 -.005h12.666zm-5.333 5h-3l-.117 .007a1 1 0 0 0 0 1.986l.117 .007h3v2h-2l-.15 .005a2 2 0 0 0 -1.844 1.838l-.006 .157v2l.005 .15a2 2 0 0 0 1.838 1.844l.157 .006h3l.117 -.007a1 1 0 0 0 0 -1.986l-.117 -.007h-3v-2h2l.15 -.005a2 2 0 0 0 1.844 -1.838l.006 -.157v-2l-.005 -.15a2 2 0 0 0 -1.838 -1.844l-.157 -.006z" /></path></svg>
        </button>

        <button id="ts_switch_pen3_button" class="active" title="Switch to Pen 3 (Alt + 3)"
              onclick="activate_pen3();" >
        <svg stroke="currentColor" fill="none" stroke-width="1.8" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M18.333 2c1.96 0 3.56 1.537 3.662 3.472l.005 .195v12.666c0 1.96 -1.537 3.56 -3.472 3.662l-.195 .005h-12.666a3.667 3.667 0 0 1 -3.662 -3.472l-.005 -.195v-12.666c0 -1.96 1.537 -3.56 3.472 -3.662l.195 -.005h12.666zm-5.333 5h-2l-.15 .005a2 2 0 0 0 -1.85 1.995a1 1 0 0 0 1.974 .23l.02 -.113l.006 -.117h2v2h-2l-.133 .007c-1.111 .12 -1.154 1.73 -.128 1.965l.128 .021l.133 .007h2v2h-2l-.007 -.117a1 1 0 0 0 -1.993 .117a2 2 0 0 0 1.85 1.995l.15 .005h2l.15 -.005a2 2 0 0 0 1.844 -1.838l.006 -.157v-2l-.005 -.15a1.988 1.988 0 0 0 -.17 -.667l-.075 -.152l-.019 -.032l.02 -.03a2.01 2.01 0 0 0 .242 -.795l.007 -.174v-2l-.005 -.15a2 2 0 0 0 -1.838 -1.844l-.157 -.006z" /></svg>
        </button>

        <button id="ts_switch_pen4_button" class="active" title="Switch to Pen 4 (Alt + 4)"
              onclick="activate_pen4();" >
        <svg stroke="currentColor" fill="none" stroke-width="1.8" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M18.333 2c1.96 0 3.56 1.537 3.662 3.472l.005 .195v12.666c0 1.96 -1.537 3.56 -3.472 3.662l-.195 .005h-12.666a3.667 3.667 0 0 1 -3.662 -3.472l-.005 -.195v-12.666c0 -1.96 1.537 -3.56 3.472 -3.662l.195 -.005h12.666zm-4.333 5a1 1 0 0 0 -.993 .883l-.007 .117v3h-2v-3l-.007 -.117a1 1 0 0 0 -1.986 0l-.007 .117v3l.005 .15a2 2 0 0 0 1.838 1.844l.157 .006h2v3l.007 .117a1 1 0 0 0 1.986 0l.007 -.117v-8l-.007 -.117a1 1 0 0 0 -.993 -.883z" /></svg>
        </button>

        <button id="ts_switch_pen4_button" class="active" title="Play Sound on card again (R)"
              onclick="PlaySound();" >
        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M6 10a7 7 0 1 1 13 3.6a10 10 0 0 1 -2 2a8 8 0 0 0 -2 3a4.5 4.5 0 0 1 -6.8 1.4" /><path d="M10 10a3 3 0 1 1 5 2.2" /></svg>
        </button>

    </div>
</div>
"""

def get_css_for_toolbar_location(location, x_offset, y_offset, orient_column, canvas_width, canvas_height, background_color):
    orient = "column" if orient_column else "row"
    switch = {
        0: f"""
                        --button-bar-pt: {y_offset}px;
                        --button-bar-pr: unset;
                        --button-bar-pb: unset;
                        --button-bar-pl: {x_offset}px;
                        --button-bar-orientation: {orient};
                        --small-canvas-height: {canvas_height};
                        --small-canvas-width: {canvas_width};
                        --background-color: {background_color};
                    """,
        1: f"""
                        --button-bar-pt: {y_offset}px;
                        --button-bar-pr: {x_offset}px;
                        --button-bar-pb: unset;
                        --button-bar-pl: unset;
                        --button-bar-orientation: {orient};
                        --small-canvas-height: {canvas_height};
                        --small-canvas-width: {canvas_width};
                        --background-color: {background_color};
                    """,
        2: f"""
                        --button-bar-pt: unset;
                        --button-bar-pr: unset;
                        --button-bar-pb: {y_offset}px;
                        --button-bar-pl: {x_offset}px;
                        --button-bar-orientation: {orient};
                        --small-canvas-height: {canvas_height};
                        --small-canvas-width: {canvas_width};
                        --background-color: {background_color};
                    """,
        3: f"""
                        --button-bar-pt: unset;
                        --button-bar-pr: {x_offset}px;
                        --button-bar-pb: {y_offset}px;
                        --button-bar-pl: unset;
                        --button-bar-orientation: {orient};
                        --small-canvas-height: {canvas_height};
                        --small-canvas-width: {canvas_width};
                        --background-color: {background_color};
                    """,
    }
    return switch.get(location, """
                        --button-bar-pt: 2px;
                        --button-bar-pr: 2px;
                        --button-bar-pb: unset;
                        --button-bar-pl: unset;
                        --button-bar-orientation: column;
                        --small-canvas-height: 500;
                        --small-canvas-width: 500;
                        --background-color: #FFFFFF00;
                    """)

def get_css_for_auto_hide(auto_hide, zen):
    return "none" if auto_hide or zen else "flex"

def get_css_for_zen_mode(hide):
    return "none" if hide else "flex"

def get_css_for_auto_hide_pointer(auto_hide):
    return "none" if auto_hide else "default"

def blackboard_css():
    return u"""
<style>
:root {
  """ + get_css_for_toolbar_location( ts_location, ts_x_offset, ts_y_offset, ts_orient_vertical, ts_small_width, ts_small_height, ts_background_color) + """
}
body {
  overflow-x: hidden; /* Hide horizontal scrollbar */
}
/*
    canvas needs touch-action: none so that it doesn't fire bogus
    pointercancel events. See:
    https://stackoverflow.com/questions/59010779/pointer-event-issue-pointercancel-with-pressure-input-pen
*/
#main_canvas, #secondary_canvas {
   z-index: 998;/* add toggle?*/
  touch-action: none;/*add toggle*/
  
  position:var(--canvas-bar-position);
  top: var(--canvas-bar-pt);
  right: var(--canvas-bar-pr);
  bottom: var(--canvas-bar-pb);
  left: var(--canvas-bar-pl);
  }
  #canvas_wrapper, #secondary_canvas {
   z-index: 999;
  }
#main_canvas, #secondary_canvas {
  background: var(--background-color);
  border-style: none;
  border-width: 1px;
}
#pencil_button_bar {
  position: fixed;
  display: """+get_css_for_zen_mode(ts_zen_mode)+""";
  flex-direction: var(--button-bar-orientation);
  opacity: .5;
  top: var(--button-bar-pt);
  right: var(--button-bar-pr);
  bottom: var(--button-bar-pb);
  left: var(--button-bar-pl);
  z-index: 8000;
  transition: .5s;
} #pencil_button_bar:hover { 
  opacity: 1;
} #pencil_button_bar > button {
  margin: 2px;
} #pencil_button_bar > button > svg {
  width: 2em;
} #pencil_button_bar > button:hover > svg {
  filter: drop-shadow(0 0 4px #000);
} #pencil_button_bar > button.active > svg > path {
  stroke: #000;
} .night_mode #pencil_button_bar > button.active > svg > path {
  stroke: #eee;
} #pencil_button_bar > button > svg > path {
  stroke: #888;
} .night_mode #pencil_button_bar > button > svg > path {
  /*stroke: #888;*/
}
.nopointer {
  cursor: """+get_css_for_auto_hide_pointer(ts_auto_hide_pointer)+""" !important;
} 
.touch_disable > button:not(:first-child){
    display: none;
}
.nopointer #pencil_button_bar
{
  display: """+get_css_for_auto_hide(ts_auto_hide, ts_zen_mode)+""";
}
</style>"""

def blackboard_js():
    config = mw.addonManager.getConfig(__name__)
    start_vis = str(config.get('start_visible', False)).lower()
    start_pen = str(config.get('default_pen_index', 1))

    return u"""
<script>
// Set from python qt ui
var visible = """ + start_vis + """;
var perfectFreehand = """ + ts_default_PerfFreehand +""";
var pressureSensitivity = """ + str(ts_pressure_sensitivity).lower() + """;
var small_canvas = """ +  str(ts_default_small_canvas).lower() + """;
var fullscreen_follow = """ + str(ts_follow).lower() + """;
var calligraphy = """ + ts_default_Calligraphy + """;
var strokeDelete = false;
var textWriting = false;
var isDeleting = false;  // Track if currently deleting (for hold mode)
var pen1Color = """ + "\'" + str(ts_pen1_color) + "\'" + """;
var pen1Width = """ + str(ts_pen1_width) + """;
var pen2Color = """ + "\'" + str(ts_pen2_color) + "\'" + """;
var pen2Width = """ + str(ts_pen2_width) + """;
var pen3Color = """ + "\'" + str(ts_pen3_color) + "\'" + """;
var pen3Width = """ + str(ts_pen3_width) + """;
var pen4Color = """ + "\'" + str(ts_pen4_color) + "\'" + """;
var pen4Width = """ + str(ts_pen4_width) + """;
var pen1Opacity = """ + str(ts_pen1_opacity) + """;
var pen2Opacity = """ + str(ts_pen2_opacity) + """;
var pen3Opacity = """ + str(ts_pen3_opacity) + """;
var pen4Opacity = """ + str(ts_pen4_opacity) + """;
var fontFamily = """ + "\'" + str(ts_font_family) + "\'" + """;
var fontSize = """ + str(ts_font_size) + """;
var fontBold = """ + str(ts_font_bold).lower() + """;
var fontItalic = """ + str(ts_font_italic).lower() + """;
var activePenIndex = """ + start_pen + """;
var convertDotStrokes = true

function forceShowCanvas() {
    if (visible === false) { // Only change if it's currently false
        visible = true;
        canvas.style.display='block';
        secondary_canvas.style.display='block';
        if (ts_visibility_button) ts_visibility_button.className = 'active';
        if (optionBar) optionBar.className = '';
    }
}

function forceHideCanvas() {
    if (visible === true) { // Only change if it's currently true
        visible = false;
        canvas.style.display='none';
        secondary_canvas.style.display='none';
        if (ts_visibility_button) ts_visibility_button.className = '';
        if (optionBar) optionBar.className = 'touch_disable';
    }
}

function getPenColorAndWidthByIndex(index){
    switch (index) {
        case 0:
            return [hexToRgba(pen1Color, pen1Opacity), pen1Width, pen1Opacity];
        break;
        case 1:
            return [hexToRgba(pen2Color, pen2Opacity), pen2Width, pen2Opacity];
        break;
        case 2:
            return [hexToRgba(pen3Color, pen3Opacity), pen3Width, pen3Opacity];
        break;
        case 3:
            return [hexToRgba(pen4Color, pen4Opacity), pen4Width, pen4Opacity];
        break;
        default:
            console.error("error too large index for pen selection")
            break;
    }
}

// Helper function to convert hex color to RGBA with opacity
function hexToRgba(hex, opacity) {
    // Remove the hash if present
    hex = hex.replace(/^#/, '');
    
    // Parse the hex values
    let r, g, b;
    if (hex.length === 3) {
        r = parseInt(hex[0] + hex[0], 16);
        g = parseInt(hex[1] + hex[1], 16);
        b = parseInt(hex[2] + hex[2], 16);
    } else if (hex.length === 6 || hex.length === 8) {
        r = parseInt(hex.substring(0, 2), 16);
        g = parseInt(hex.substring(2, 4), 16);
        b = parseInt(hex.substring(4, 6), 16);
    } else {
        return hex; // Return as-is if not a valid hex color
    }
    
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// HTML references
var canvas = document.getElementById('main_canvas');
var wrapper = document.getElementById('canvas_wrapper');
var textBox = document.getElementById('AnkiDrawTextBox');
var optionBar = document.getElementById('pencil_button_bar');
var ts_undo_button = document.getElementById('ts_undo_button');
var ts_redo_button = document.getElementById('ts_redo_button');
var ctx = canvas.getContext('2d');
var secondary_canvas = document.getElementById('secondary_canvas');
var secondary_ctx = secondary_canvas.getContext('2d');
var ts_visibility_button = document.getElementById('ts_visibility_button');
var ts_kanji_button = document.getElementById('ts_kanji_button');
var ts_text_button = document.getElementById('ts_text_button');
var ts_perfect_freehand_button = document.getElementById('ts_perfect_freehand_button');
var ts_stroke_delete_button = document.getElementById('ts_stroke_delete_button');
var ts_switch_fullscreen_button = document.getElementById('ts_switch_fullscreen_button');


var ts_visibility_button_path1 = document.querySelector('#ts_visibility_button > svg > path');
var ts_visibility_button_path2 = document.querySelector('#ts_visibility_button > svg > path:nth-child(2)');

var ts_switch_pen1_button_path = document.querySelector('#ts_switch_pen1_button > svg > path');
var ts_switch_pen2_button_path = document.querySelector('#ts_switch_pen2_button > svg > path');
var ts_switch_pen3_button_path = document.querySelector('#ts_switch_pen3_button > svg > path');
var ts_switch_pen4_button_path = document.querySelector('#ts_switch_pen4_button > svg > path');

// Arrays to save point values from strokes
if (!visible) {
    canvas.style.display = 'none';
    secondary_canvas.style.display = 'none';
    
    if (ts_visibility_button) {
        ts_visibility_button.className = '';
    }
    
    if (optionBar) {
        optionBar.className = 'touch_disable';
    }
}
var stroke_cache = [ ];
var lineHistory = [ ] // contains history of currentAction Items, defined below
var redoStack = [ ]
let textCursorVisible = true;
let cursorBlinkInterval;

// Current stroke in progress
var currentAction = {
    points: [],
    color: '',
    width: '',
    opacity: '',
    visible: true,
    type: '', // 'simple' 'L', 'perfect' 'P', 'calligraphy' 'C', Delete 'D', Clear 'X'
    deletedList: [] // used only for delete actions
};

var index = 0;

canvas.onselectstart = function() { return false; };
secondary_canvas.onselectstart = function() { return false; };
wrapper.onselectstart = function() { return false; };

function PlaySound(){
    var selectors = document.querySelectorAll(".soundLink, .replaybutton")
    if (selectors) { selectors[index++ % selectors.length].click(); }
}
function recolor_based_on_active_pen()
{   
    var color = getPenColorAndWidthByIndex(activePenIndex)[0]

    ts_visibility_button_path1.style.stroke = color
    ts_visibility_button_path2.style.stroke = color

    ts_switch_pen1_button_path.style.stroke = pen1Color
    ts_switch_pen2_button_path.style.stroke = pen2Color
    ts_switch_pen3_button_path.style.stroke = pen3Color
    ts_switch_pen4_button_path.style.stroke = pen4Color
}

function activate_pen1()
{
    activePenIndex = 0
    update_pen_settings();
}

function activate_pen2()
{
    activePenIndex = 1
    update_pen_settings();
}

function activate_pen3()
{
    activePenIndex = 2
    update_pen_settings();
}

function activate_pen4()
{
    activePenIndex = 3
    update_pen_settings();
}

function reset_drawing_modes()
{
    ts_kanji_button.className = '';
    ts_perfect_freehand_button.className = '';
    ts_stroke_delete_button.className = '';
    ts_text_button.className = '';
    calligraphy = false;
    perfectFreehand = false;
    strokeDelete = false
    textWriting = false;
    reset_to_main_pen_settings()
    ts_redraw()
}

ts_kanji_button_class = '';
ts_perfect_freehand_button_class = '';
ts_stroke_delete_button_class = '';
ts_text_button_class = '';
calligraphy_activated = false;
perfectFreehand_activated = false;
strokeDelete_activated = false
textWriting_activated = false;

function save_drawing_modes_for_delete()
{
    ts_kanji_button_class = ts_kanji_button.className;
    ts_perfect_freehand_button_class = ts_perfect_freehand_button.className;
    ts_text_button_class = ts_text_button.className;
    calligraphy_activated = calligraphy
    perfectFreehand_activated = perfectFreehand
    textWriting_activated = textWriting
    reset_to_main_pen_settings()
    ts_redraw()
}

function restore_drawing_modes_for_delete()
{
    ts_kanji_button.className = ts_kanji_button_class
    ts_perfect_freehand_button.className = ts_perfect_freehand_button_class
    ts_text_button.className = ts_text_button_class
    calligraphy = calligraphy_activated
    perfectFreehand = perfectFreehand_activated
    textWriting = textWriting_activated
    reset_to_main_pen_settings()
    ts_redraw()
}

function switch_perfect_freehand()
{
    stop_drawing();
    temp = !perfectFreehand;
    reset_drawing_modes()
    perfectFreehand = temp;
    if(perfectFreehand)
    {
        ts_perfect_freehand_button.className = 'active';
    }
    else{
        ts_perfect_freehand_button.className = '';
    }
}

function switch_calligraphy_mode()
{
    stop_drawing();
    temp = !calligraphy;
    reset_drawing_modes()
    calligraphy = temp;
    if(calligraphy)
    {
        ts_kanji_button.className = 'active';
    }
    else{
        ts_kanji_button.className = '';
    }
}
function switch_text_writing_mode()
{
    stop_drawing();
    // In toggle mode, toggle the textWriting boolean
    temp = !textWriting;
    reset_drawing_modes()
    textWriting = temp;
    if(textWriting)
    {
        textBox.focus()
        ts_text_button.className = 'active';
    }
    else{
        textBox.blur()
        ts_text_button.className = '';
    }
}
function switch_stroke_delete_mode()
{
    stop_drawing();
    
    // In toggle mode, toggle the strokeDelete boolean
    strokeDelete = !strokeDelete;
    if(strokeDelete || isDeleting)
    {
        save_drawing_modes_for_delete()
        ts_stroke_delete_button.className = 'active';
    }
    else{
        restore_drawing_modes_for_delete()
        ts_stroke_delete_button.className = '';
    }
}
function enter_stroke_delete_mode()
{
    stop_drawing();
    strokeDelete = true;
    isDeleting = true;
    if(strokeDelete || isDeleting)
    {
        save_drawing_modes_for_delete()
        ts_stroke_delete_button.className = 'active';
    }
    else{
        restore_drawing_modes_for_delete()
        ts_stroke_delete_button.className = '';
    }
}
function exit_stroke_delete_mode()
{
    stop_drawing();
    strokeDelete = false;
    isDeleting = false
    if(strokeDelete || isDeleting)
    {
        save_drawing_modes_for_delete()
        ts_stroke_delete_button.className = 'active';
    }
    else{
        restore_drawing_modes_for_delete()
        ts_stroke_delete_button.className = '';
    }
}


function switch_small_canvas()
{
    stop_drawing();
    
    small_canvas = !small_canvas;
    if(!small_canvas)
    {
        ts_switch_fullscreen_button.className = 'active';
    }
    else{
        ts_switch_fullscreen_button.className = '';
    }
    resize();
}

function switch_visibility()
{
	stop_drawing();
    if (!visible) {
        canvas.style.display='none';
        secondary_canvas.style.display='none';
        ts_visibility_button.className = '';
        optionBar.className = 'touch_disable';
    }
    else
    {
        canvas.style.display='block';
        secondary_canvas.style.display=canvas.style.display;
        ts_visibility_button.className = 'active';
        optionBar.className = '';
    }
    visible = !visible;
}

//Initialize event listeners at the start;
canvas.addEventListener("pointerdown", pointerDownLine);
canvas.addEventListener("pointermove", pointerMoveLine);
secondary_canvas.addEventListener("pointerdown", pointerDownLine);
secondary_canvas.addEventListener("pointermove", pointerMoveLine);
window.addEventListener("pointerup", pointerUpLine);
canvas.addEventListener("pointerdown", pointerDownCaligraphy);
canvas.addEventListener("pointermove", pointerMoveCaligraphy);
secondary_canvas.addEventListener("pointerdown", pointerDownCaligraphy);
secondary_canvas.addEventListener("pointermove", pointerMoveCaligraphy);
window.addEventListener("pointerup", pointerUpCaligraphy);
canvas.addEventListener("pointerdown", pointerDownStrokeDelete);
canvas.addEventListener("pointermove", pointerMoveStrokeDelete);
secondary_canvas.addEventListener("pointerdown", pointerDownStrokeDelete);
secondary_canvas.addEventListener("pointermove", pointerMoveStrokeDelete);
window.addEventListener("pointerup", pointerUpStrokeDelete);

window.addEventListener("pointerup", pointerDownLineText);
window.addEventListener("pointerdown", pointerDownLineText);

function resize() {
    
    var card = document.getElementsByClassName('card')[0]
    
    // Run again until card is loaded
    if (!card){
        window.setTimeout(resize, 100)
        return;
        
    }
    // Check size of page without canvas
    canvas_wrapper.style.display='none';
    canvas.style["border-style"] = "none";
    secondary_canvas.style["border-style"] = "none";
    document.documentElement.style.setProperty('--canvas-bar-pt', '0px');
    document.documentElement.style.setProperty('--canvas-bar-pr', '0px');
    document.documentElement.style.setProperty('--canvas-bar-pb', 'unset');
    document.documentElement.style.setProperty('--canvas-bar-pl', 'unset');
    document.documentElement.style.setProperty('--canvas-bar-position', 'absolute');
    
    if(!small_canvas && !fullscreen_follow){
        ctx.canvas.width = Math.max(card.scrollWidth, document.documentElement.clientWidth);
        ctx.canvas.height = Math.max(document.documentElement.scrollHeight, document.documentElement.clientHeight);        
    }
    else if(small_canvas){
        ctx.canvas.width = Math.min(document.documentElement.clientWidth, 
        getComputedStyle(document.documentElement).getPropertyValue('--small-canvas-width'));
        ctx.canvas.height = Math.min(document.documentElement.clientHeight, 
        getComputedStyle(document.documentElement).getPropertyValue('--small-canvas-height'));
        canvas.style["border-style"] = "dashed";
        secondary_canvas.style["border-style"] = "dashed";
        document.documentElement.style.setProperty('--canvas-bar-pt', 
        getComputedStyle(document.documentElement).getPropertyValue('--button-bar-pt'));
        document.documentElement.style.setProperty('--canvas-bar-pr', 
        getComputedStyle(document.documentElement).getPropertyValue('--button-bar-pr'));
        document.documentElement.style.setProperty('--canvas-bar-pb', 
        getComputedStyle(document.documentElement).getPropertyValue('--button-bar-pb'));
        document.documentElement.style.setProperty('--canvas-bar-pl', 
        getComputedStyle(document.documentElement).getPropertyValue('--button-bar-pl'));
        document.documentElement.style.setProperty('--canvas-bar-position', 'fixed');
    }
    else{
        document.documentElement.style.setProperty('--canvas-bar-position', 'fixed');
        ctx.canvas.width = document.documentElement.clientWidth-1;
        ctx.canvas.height = document.documentElement.clientHeight-1;
    }
    secondary_ctx.canvas.width = ctx.canvas.width;
    secondary_ctx.canvas.height = ctx.canvas.height;
    canvas_wrapper.style.display='block';
    
    
    
    /* Get DPR with 1 as fallback */
    var dpr = window.devicePixelRatio || 1;
    
    /* CSS size is the same */
    canvas.style.height = ctx.canvas.height + 'px';
    wrapper.style.width = ctx.canvas.width + 'px';
    secondary_canvas.style.height = canvas.style.height;
    secondary_canvas.style.width = canvas.style.width;
    
    /* Increase DOM size and scale */
    ctx.canvas.width *= dpr;
    ctx.canvas.height *= dpr;
    ctx.scale(dpr, dpr);
    secondary_ctx.canvas.width *= dpr;
    secondary_ctx.canvas.height *= dpr;
    secondary_ctx.scale(dpr, dpr);
    
	update_pen_settings()
    
}


window.addEventListener('resize', resize);
window.addEventListener('load', resize);
window.requestAnimationFrame(draw_last_line_segment);

var isPointerDown = false;
var mouseX = 0;
var mouseY = 0;

function update_pen_settings(){
    stop_drawing()
    var pen = getPenColorAndWidthByIndex(activePenIndex);

    if(ctx.lineJoin != 'round'){
        ctx.lineJoin = ctx.lineCap = 'round';
        secondary_ctx.lineJoin = secondary_ctx.lineCap = ctx.lineJoin;
    }   
    if(ctx.lineWidth != pen[1]) {
        ctx.lineWidth = pen[1]; // pen Width
        secondary_ctx.lineWidth = ctx.lineWidth
    }
    if(ctx.strokeStyle != pen[0]){
        ctx.strokeStyle = ctx.fillStyle = pen[0]; // pen color
        
        
    } 
    var pencolorNoAlpha = pen[0].replace(/[\d\.]+\)$/g, '1)');
    if(secondary_ctx.strokeStyle != pencolorNoAlpha){
        secondary_ctx.strokeStyle = secondary_ctx.fillStyle = pencolorNoAlpha;
    }
    
    if(secondary_canvas.style.opacity != pen[2]) secondary_canvas.style.opacity = pen[2]
    if(canvas.style.opacity != pen[2]) canvas.style.opacity = pen[2]
    
    recolor_based_on_active_pen()
    ts_redraw()
}

function reset_to_main_pen_settings(){
    var pen = getPenColorAndWidthByIndex(activePenIndex);
    if(ctx.lineJoin != 'round'){
        ctx.lineJoin = ctx.lineCap = 'round';
        secondary_ctx.lineJoin = secondary_ctx.lineCap = ctx.lineJoin;
    }   
    if(ctx.lineWidth != pen[1]) {
        ctx.lineWidth = pen[1]; // pen Width
        secondary_ctx.lineWidth = ctx.lineWidth
    }
    if(ctx.strokeStyle != pen[0]){
        ctx.strokeStyle = ctx.fillStyle = pen[0]; // pen color
    } 
    var pencolorNoAlpha = pen[0].replace(/[\d\.]+\)$/g, '1)');
    if(secondary_ctx.strokeStyle != pencolorNoAlpha){
        secondary_ctx.strokeStyle = secondary_ctx.fillStyle = pencolorNoAlpha;
    }
    
    if(secondary_canvas.style.opacity != pen[2]) secondary_canvas.style.opacity = pen[2]
    if(canvas.style.opacity != pen[2]) canvas.style.opacity = pen[2]
    
}

function update_line_draw_settings(color, width, opacity){
    ctx.lineJoin = ctx.lineCap = 'round';
    if(ctx.lineWidth != width)ctx.lineWidth = width
    if(ctx.fillStyle != color)ctx.fillStyle = ctx.strokeStyle = color
}

function get_no_alpha(line_color){
    return ctx.strokeStyle.replace(/[\d\.]+\)$/g, '1)');
}

function ts_undo(){
	stop_drawing();
    if(lineHistory.length>0){
        var poppedAction = lineHistory.pop()
        redoStack.push(poppedAction)
        ts_redo_button.className = "active";
        stroke_cache[lineHistory.length] = null;
        switch (poppedAction.type) {
            case 'C'://Calligraphy
                break;
            case 'L'://Simple Lines
                break;
            case 'P'://Perfect Lines
                break;
            case 'D'://Delete Stroke Lines
                poppedAction.deletedList.forEach( deletedIndex => { lineHistory[deletedIndex].visible = true } )
                break;
            case 'X'://Clear actions
                break;
            case 'T'://Text Writing actions
                break;
            default://how did you get here??
                break;
        }
    }

    if(!lineHistory.length)
    {
        ts_undo_button.className = ""
    }
    ts_redraw()
}
function ts_redo() {
    stop_drawing();
    if (redoStack.length < 1) return;
    
    var redoAction = redoStack.pop();
    readd_action_to_history(redoAction)
    ts_undo_button.className = "active";
    switch (redoAction.type) {
        case 'C'://Calligraphy
            break;
        case 'L'://Simple Lines
            break;
        case 'D'://Delete Stroke Lines
            redoAction.deletedList.forEach( deletedIndex => { lineHistory[deletedIndex].visible = false } )
            break;
        case 'X'://Delete Stroke Lines
            break;
        default://how did you get here??
            break;
    }
    
    ts_redraw();
    if (redoStack.length === 0) {
        ts_redo_button.className = "";
    }
}

function ts_redraw() {
	pleaseRedrawEverything = true;
}

function ts_clear() {
	pleaseRedrawEverything = true;
    fullClear = true;
}

function clear_canvas()
{
	//don't continue to put points into an empty array(pointermove) if clearing while drawing on the canvas
	stop_drawing();
    reset_history();
    reset_redo()
	ts_clear();
}

function add_clear_marker()
{
	//don't continue to put points into an empty array(pointermove) if clearing while drawing on the canvas
	stop_drawing();
    if(lineHistory.length && lineHistory[lineHistory.length-1].type != 'X')add_action_to_history({ type: 'X'})
	ts_clear();
}

function add_action_to_history(action){
    ts_undo_button.className = "active"
    lineHistory.push(action)
    currentAction = {}
    reset_redo()
}

function readd_action_to_history(action){
    ts_undo_button.className = "active"
    lineHistory.push(action)
    currentAction = {}
}

function reset_redo(){
    redoStack = [];
    ts_redo_button.className = "";
}

function reset_history(){
    lineHistory = [];
    stroke_cache = [];
    ts_undo_button.className = "";
}

function stop_drawing() {
    reset_to_main_pen_settings()
    submitCurrentText()
    isPointerDown = false;
	drawingWithPressurePenOnly = false;
}

function start_drawing() {
    submitCurrentText()
    isPointerDown = true;
    reset_redo()
}

function draw_last_line_segment() {
    window.requestAnimationFrame(draw_last_line_segment);
    draw_upto_latest_point_async(nextLine, nextPoint, nextStroke);
}

var nextLine = 0;
var nextPoint = 0;
var nextStroke = 0;
var p1,p2,p3;

function is_last_path_and_currently_drawn(i){
    return (lineHistory.length-1 < i)//the path is complete unless its the last of the array and the pointer is still down
}

function all_drawing_finished(i){
    return (lineHistory.length-1 >= i)//the path is complete unless its the last of the array and the pointer is still down
}

async function draw_path_at_some_point_async(startX, startY, midX, midY, endX, endY, lineWidth) {
		ctx.beginPath();
		ctx.moveTo((startX + (midX - startX) / 2), (startY + (midY - startY)/ 2));//midpoint calculation for x and y
		ctx.quadraticCurveTo(midX, midY, (midX + (endX - midX) / 2), (midY + (endY - midY)/ 2));
        ctx.lineWidth = lineWidth;
		ctx.stroke();
};
async function draw_secondary_path_at_some_point_async(startX, startY, midX, midY, endX, endY, lineWidth) {
		secondary_ctx.beginPath();
		secondary_ctx.moveTo((startX + (midX - startX) / 2), (startY + (midY - startY)/ 2));//midpoint calculation for x and y
		secondary_ctx.quadraticCurveTo(midX, midY, (midX + (endX - midX) / 2), (midY + (endY - midY)/ 2));
        secondary_ctx.lineWidth = lineWidth;
		secondary_ctx.stroke();
};

var pleaseRedrawEverything = false;
var fullClear = false;

async function draw_upto_latest_point_async(startLine, startPoint, startStroke){
	var fullRedraw = false;//keep track if this call started a full redraw to unset pleaseRedrawEverything flag later.
	if (pleaseRedrawEverything) {// erase everything and draw from start
        fullRedraw = true;
        startLine = 0;
        startPoint = 0;
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
	}
    for (let index = lineHistory.length-1; index > 0; index--) {//go thrught the history in reverse
        if(lineHistory[index].type == 'X'){// the first clear we find is where we should start from 
            if(index>startLine)startLine = index // if it's later than what we intend to draw
            break;
        }
    }
    for(var i = startLine; i < lineHistory.length; i++){ //Draw
        actionToDraw = lineHistory[i]
        if(!actionToDraw.visible) {
            nextPoint = 0;
            continue;
        }

        update_line_draw_settings(actionToDraw.color, actionToDraw.width, actionToDraw.opacity)
        switch (actionToDraw.type) {
            case 'C'://Calligraphy
                    var calligraphyStroke = !stroke_cache[i] ? new Stroke(fitStroke(actionToDraw.points)) : stroke_cache[i]
                    stroke_cache[i] = calligraphyStroke
                    calligraphyStroke.draw(actionToDraw.width, ctx);
                break;
            case 'L'://Simple Lines
                ///0,0,0; 0,0,1; 0,1,2 or x+1,x+2,x+3
                //take the 2 previous points in addition to current one at the start of the loop.
                p2 = actionToDraw.points[startPoint > 1 ? startPoint-2 : 0];
                p3 = actionToDraw.points[startPoint > 0 ? startPoint-1 : 0];
                for(var j = startPoint; j < actionToDraw.points.length; j++){
                    nextPoint = j + 1;
                    p1 = p2;
                    p2 = p3;
                    p3 = actionToDraw.points[j];
                    var save = ctx.strokeStyle
                    //sadly this doesnt work well with windows, as it leaves circle outlines due to alpha blending, so abandon per stroke opacty dreams
                    // update_line_draw_settings(get_no_alpha(save), actionToDraw.width, actionToDraw.opacity)
                    // ctx.globalCompositeOperation = "destination-out";
                    // draw_path_at_some_point_async(p1[0],p1[1],p2[0],p2[1],p3[0],p3[1],p3[3]);

                    update_line_draw_settings(get_no_alpha(save), actionToDraw.width, actionToDraw.opacity)

                    ctx.globalCompositeOperation = "source-over";
                    draw_path_at_some_point_async(p1[0],p1[1],p2[0],p2[1],p3[0],p3[1],p3[3]);
                }
                
                break;
            case 'P'://Perfect Lines
                var path = !stroke_cache[i] ? new Path2D(getFreeDrawSvgPath(actionToDraw.points, actionToDraw.width, true)) : stroke_cache[i]
                stroke_cache[i] = path
                var save = ctx.strokeStyle
                // update_line_draw_settings(get_no_alpha(save), actionToDraw.width, actionToDraw.opacity)
                // ctx.globalCompositeOperation = "destination-out";
                // ctx.fill(path);

                update_line_draw_settings(get_no_alpha(save), actionToDraw.width, actionToDraw.opacity)
                ctx.globalCompositeOperation = "source-over";
                ctx.fill(path);
                break;
            case 'D'://Delete Stroke Lines
                break;
            case 'X'://Clear Screen
                break;
            case 'T'://Write Text
                var save = ctx.strokeStyle
                // update_line_draw_settings(get_no_alpha(save), actionToDraw.width, actionToDraw.opacity)
                // ctx.globalCompositeOperation = "destination-out";
                // drawTextFromAction(ctx, actionToDraw)

                update_line_draw_settings(get_no_alpha(save), actionToDraw.width, actionToDraw.opacity)
                ctx.globalCompositeOperation = "source-over";
                drawTextFromAction(ctx, actionToDraw)
                break;
            default://how did you get here??
                break;
        }
        //post loop cleanup
        if(all_drawing_finished(i)){
            nextLine = lineHistory.length;
            nextPoint = 0;
        }
        else{
            if(lineHistory.length == 0){
                nextLine = 0;
            }
            else{
                nextLine = lineHistory.length-1;
            }
        }
    }
    if(!strokeDelete)reset_to_main_pen_settings()
    
	if (fullRedraw) {//finished full redraw, now can unset redraw all flag so no more full redraws until necessary
        pleaseRedrawEverything = false;
        fullRedraw = false;
        nextPoint = lineHistory.length == 0 ? 0 : nextPoint;//reset next point if out of lines
        nextLine = lineHistory.length == 0 ? 0 : lineHistory.length
        if(fullClear){// start again from 0.
            nextLine = 0;
            fullClear = false;
        }
	}
}

var drawingWithPressurePenOnly = false; // hack for drawing with 2 main pointers when using a presure sensitive pen

function calculateClearBox(pointsArray) {
    if (!pointsArray.length) return {x: 0, y: 0, width: 0, height: 0};
    
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;
    
    pointsArray.forEach(point => {
        if (point[0] < minX) minX = point[0];
        if (point[0] > maxX) maxX = point[0];
        if (point[1] < minY) minY = point[1];
        if (point[1] > maxY) maxY = point[1];
    });
    
    // Add some padding for line caps/width
    const padding = 1;
    
    return {
        x: minX - padding,
        y: minY - padding,
        width: (maxX - minX) + padding * 2,
        height: (maxY - minY) + padding * 2
    };
}
function drawCursor(x, y) {
    secondary_ctx.beginPath();
    secondary_ctx.moveTo(x, y);
    secondary_ctx.lineTo(x, y + fontSize);
    secondary_ctx.strokeStyle = 'red';
    secondary_ctx.lineWidth = 2;
    secondary_ctx.stroke();
}

function startCursorBlink() {
    clearInterval(cursorBlinkInterval);
    drawTextOnCanvas()
    cursorBlinkInterval = setInterval(() => {
        textCursorVisible = !textCursorVisible;
        drawTextOnCanvas();
    }, 500);
}

function createBoxWithDiagonalPoints(action) {
    const lines = action.text.split(/(?<!\\\\)\\n/);
    const allBoxPoints = [];
    
    const padding = 1;
    const spacing = 8;
    const lineHeight = calculateLineHeight(action.fontSize);

    var fontString = "";
    if (action.fontBold) fontString += "bold ";
    if (action.fontItalic) fontString += "italic ";
    fontString += action.fontSize + "px " + action.fontFamily;

    ctx.font = fontString;
    let currentY = action.y;
    
    // Process each line separately
    for (let i = 0; i < lines.length; i++) {
        const lineText = lines[i];
        
        const textWidth = ctx.measureText(lineText).width;
        
        // Calculate box for this line
        const x = action.x - padding;
        const y = currentY - padding;
        const width = textWidth + padding * 2;
        const height = action.fontSize + padding * 2;
        
        // Start with box corner points for this line
        const points = [
            [x, y],
            [x + width, y],  
            [x + width, y + height],
            [x, y + height]
        ];
        
        // Calculate diagonal lines for this box
        const diagonalLength = Math.sqrt(width * width + height * height);
        
        // Generate lines in both directions
        const directions = [
            // Direction 1: y = x + b (top-left to bottom-right)
            (i) => ({
                startX: x + i,
                startY: y,
                endX: x + i + diagonalLength,
                endY: y + diagonalLength,
                isOpposite: false
            }),
            // Direction 2: y = -x + b (top-right to bottom-left)  
            (i) => ({
                startX: x + diagonalLength - i,
                startY: y,
                endX: x - i,
                endY: y + diagonalLength,
                isOpposite: true
            })
        ];
        
        directions.forEach(getLine => {
            for (let j = -diagonalLength; j < diagonalLength; j += spacing) {
                const line = getLine(j);
                const intersection = lineIntersectsRect(
                    line.startX, line.startY, line.endX, line.endY, 
                    x, y, width, height,
                    line.isOpposite
                );
                
                if (intersection) {
                    const [segmentStart, segmentEnd] = intersection;
                    points.push(segmentStart, segmentEnd);
                }
            }
        });
        
        // Add this line's box points to the combined array
        allBoxPoints.push(...points);
        
        // Move Y position down for next line
        currentY += lineHeight;
    }
    
    return allBoxPoints;
}

// Updated unified intersection function
function lineIntersectsRect(x1, y1, x2, y2, rectX, rectY, rectW, rectH, isOpposite = false) {
    // Line equation: y = mx + b where m = 1 for normal, m = -1 for opposite
    const m = isOpposite ? -1 : 1;
    const b = y1 - m * x1;
    
    const intersections = [];
    
    // Intersection with left edge (x = rectX)
    const yAtLeft = m * rectX + b;
    if (yAtLeft >= rectY && yAtLeft <= rectY + rectH) {
        if (x1 <= rectX && rectX <= x2 || x2 <= rectX && rectX <= x1) {
            intersections.push([rectX, yAtLeft]);
        }
    }
    
    // Intersection with right edge (x = rectX + rectW)
    const yAtRight = m * (rectX + rectW) + b;
    if (yAtRight >= rectY && yAtRight <= rectY + rectH) {
        if (x1 <= rectX + rectW && rectX + rectW <= x2 || 
            x2 <= rectX + rectW && rectX + rectW <= x1) {
            intersections.push([rectX + rectW, yAtRight]);
        }
    }
    
    // Intersection with top edge (y = rectY)
    const xAtTop = (rectY - b) / m;
    if (xAtTop >= rectX && xAtTop <= rectX + rectW) {
        if (y1 <= rectY && rectY <= y2 || y2 <= rectY && rectY <= y1) {
            intersections.push([xAtTop, rectY]);
        }
    }
    
    // Intersection with bottom edge (y = rectY + rectH)
    const xAtBottom = (rectY + rectH - b) / m;
    if (xAtBottom >= rectX && xAtBottom <= rectX + rectW) {
        if (y1 <= rectY + rectH && rectY + rectH <= y2 || 
            y2 <= rectY + rectH && rectY + rectH <= y1) {
            intersections.push([xAtBottom, rectY + rectH]);
        }
    }
    
    if (intersections.length >= 2) {
        intersections.sort((a, b) => a[0] - b[0]);
        return [intersections[0], intersections[1]];
    }
    
    return null;
}

function submitCurrentText() {
    if (currentAction && currentAction.text && currentAction.text.length > 0) {

        // Create and save box around the text
        currentAction.points = createBoxWithDiagonalPoints(currentAction);
        // Save the text entry
        add_action_to_history(currentAction)
        
        // Clear current entry
        textBox.blur()
        secondary_ctx.clearRect(0, 0, canvas.width, canvas.height);   
    }
    textBox.value = ""
}


function pointerDownLineText(e) {
    if (!e.isPrimary || !textWriting) { return; }
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;
    
    submitCurrentText();
    
    var pen = getPenColorAndWidthByIndex(activePenIndex);
    currentAction = {
        points: [],
        x: clickX,
        y: clickY,
        text: "",
        color: pen[0],
        width: pen[1],
        opacity: pen[2],
        visible: true,
        type: 'T', // 'text'
        fontFamily: fontFamily,
        fontSize: fontSize,
        fontBold: fontBold,
        fontItalic: fontItalic
    };
    textBox.focus()
};
// Prevent arrow key cursor movement
textBox.addEventListener('keydown', e => {
    if(!textWriting)return
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
        e.preventDefault();
    }
    else if (e.key === 'Escape') {
        submitCurrentText();
    }
    else if (e.altKey){
        e.preventDefault()
    }
});
textBox.addEventListener('input', () => {
    if (!currentAction || !textWriting) return;
    
    currentAction.text = textBox.value
    drawTextOnCanvas();
});

textBox.addEventListener('focus', () => startCursorBlink());
textBox.addEventListener('blur', () => {clearInterval(cursorBlinkInterval); submitCurrentText();});
// Prevent canvas click from stealing focus
canvas_wrapper.addEventListener('pointerdown', e => {
    if(!textWriting)return;
    e.preventDefault(); // Prevent focus loss    
    // Ensure textarea stays focused
    textBox.focus();
});

// Helper functions for calculations
function calculateLineHeight(fontSize) {
    // Line height = font size + appropriate spacing
    // For small fonts: add more relative spacing
    // For large fonts: add less relative spacing
    if (fontSize < 12) {
        return fontSize + 8; // More spacing for small text
    } else if (fontSize < 24) {
        return fontSize + 6; // Medium spacing
    } else {
        return fontSize + 4; // Less spacing for large text
    }
}

function calculateCursorOffset(fontSize) {
    // Cursor offset should be proportional to font size
    return Math.max(1, Math.floor(fontSize / 15));
}

function drawTextOnCanvas() {
    if(!textWriting)return;
    secondary_ctx.clearRect(0, 0, canvas.width, canvas.height);
        
    // Draw current entry text (dynamic)
    if (currentAction) {
        var lines = drawTextFromAction(secondary_ctx, currentAction)
        
        // Draw cursor if visible
        if (textCursorVisible) {
            const textWidth = lines ? secondary_ctx.measureText(lines[lines.length-1]).width + calculateCursorOffset(currentAction.fontSize) : 0;
            var currentLine = lines ? lines.length-1 : 0
            drawCursor(currentAction.x + textWidth, currentAction.y + currentLine * calculateLineHeight(currentAction.fontSize));
        }
    }
}

function drawTextFromAction(paramCtx, action){
    var lines = null
    if (action && action.type == 'T') {
        if(action.text){
            var lines = action.text.split(/(?<!\\\\)\\n/);//this is an escaped string as javascript is passed as a string into the python code
            for(var i = 0; i< lines.length; i++){
                var fontString = "";
                if (action.fontBold) fontString += "bold ";
                if (action.fontItalic) fontString += "italic ";
                fontString += action.fontSize + "px " + action.fontFamily;
                
                paramCtx.font = fontString;
                paramCtx.textBaseline = 'top';
                paramCtx.fillText(lines[i], action.x , action.y + i * calculateLineHeight(action.fontSize));
            }
        }
    }
    return lines
}

function pointerDownLine(e) {
    wrapper.classList.add('nopointer');
	if (!e.isPrimary || calligraphy || strokeDelete || textWriting) { return; }
	if (e.pointerType[0] == 'p' && pressureSensitivity) { drawingWithPressurePenOnly = true }
	else if ( drawingWithPressurePenOnly) { return; }
    var pen = getPenColorAndWidthByIndex(activePenIndex);
    if(!isPointerDown){
        event.preventDefault();
        currentAction = {
            points: [],
            color: pen[0],
            width: pen[1],
            opacity: pen[2],
            visible: true,
            type: perfectFreehand ? 'P' : 'L', // 'simple', 'perfect'
        };
        currentAction.points.push([
			e.offsetX,
			e.offsetY,
            (e.pointerType[0] == 'p' && pressureSensitivity) ? e.pressure : 2,//set pressure for perfect draw
			(e.pointerType[0] == 'p' && pressureSensitivity) ? (1.0 + e.pressure * currentAction.width * 2) : currentAction.width]);//set pressure for simple lines
        if(perfectFreehand){
            const box = calculateClearBox(currentAction.points);
            secondary_ctx.clearRect(box.x, box.y, box.width, box.height);
            var path = new Path2D(getFreeDrawSvgPath(currentAction.points, currentAction.width, true)) 
            secondary_ctx.fill(path)
        }
        else{
            draw_secondary_path_at_some_point_async(currentAction.points[0][0],currentAction.points[0][1],currentAction.points[0][0],currentAction.points[0][1],currentAction.points[0][0],currentAction.points[0][1],currentAction.points[0][3])
        }
        start_drawing();
    }
}

function pointerMoveLine(e) {
	if (!e.isPrimary || calligraphy || strokeDelete || textWriting) { return; }
	if (e.pointerType[0] != 'p' && drawingWithPressurePenOnly) { return; }
    var pen = getPenColorAndWidthByIndex(activePenIndex);
    if (isPointerDown) {
        currentAction.points.push([
			e.offsetX,
			e.offsetY,
            (e.pointerType[0] == 'p' && pressureSensitivity) ? e.pressure : 2,
			(e.pointerType[0] == 'p' && pressureSensitivity) ? (1.0 + e.pressure * currentAction.width * 2) : currentAction.width]);
        if(perfectFreehand){
            const box = calculateClearBox(currentAction.points);
            secondary_ctx.clearRect(box.x, box.y, box.width, box.height);
            var path = new Path2D(getFreeDrawSvgPath(currentAction.points, currentAction.width, true)) 
            secondary_ctx.fill(path)
        }
        else{
            p1 = currentAction.points.length > 2 ? currentAction.points.length-3 : 0;
            p2 = currentAction.points.length > 1 ? currentAction.points.length-2 : 0;
            p3 = currentAction.points.length - 1;
            draw_secondary_path_at_some_point_async(currentAction.points[p1][0],currentAction.points[p1][1],currentAction.points[p2][0],currentAction.points[p2][1],currentAction.points[p3][0],currentAction.points[p3][1],currentAction.points[p3][3])
        }
    }
}

function pointerUpLine(e) {
    wrapper.classList.remove('nopointer');
    /* Needed for the last bit of the drawing. */
	if (!e.isPrimary || calligraphy || strokeDelete || textWriting) { return; }
	if (e.pointerType[0] != 'p' && drawingWithPressurePenOnly) { return; }
    var pen = getPenColorAndWidthByIndex(activePenIndex);
    if (isPointerDown) {
        currentAction.points.push([
			e.offsetX,
			e.offsetY,
            (e.pointerType[0] == 'p' && pressureSensitivity) ? e.pressure : 2,
			(e.pointerType[0] == 'p' && pressureSensitivity) ? (1.0 + e.pressure * currentAction.width * 2) : currentAction.width]);

        if(perfectFreehand){
            const box = calculateClearBox(currentAction.points);
            secondary_ctx.clearRect(box.x, box.y, box.width, box.height);
            var path = new Path2D(getFreeDrawSvgPath(currentAction.points, currentAction.width,true)) 
            secondary_ctx.fill(path)
        }
        else{
            p1 = currentAction.points.length > 2 ? currentAction.points.length-3 : 0;
            p2 = currentAction.points.length > 1 ? currentAction.points.length-2 : 0;
            p3 = currentAction.points.length - 1;
            draw_secondary_path_at_some_point_async(currentAction.points[p1][0],currentAction.points[p1][1],currentAction.points[p2][0],currentAction.points[p2][1],currentAction.points[p3][0],currentAction.points[p3][1],currentAction.points[p3][3])
        }
        add_action_to_history(currentAction)
        secondary_ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);//clear the guide line in second canvas
    } 
	stop_drawing();
    
}

var tempColor = ""; // The variable to change
var eraseMode = false // Are we currently drawing the erase line?
var intervalId = null; // To track the interval

// Function to update the variable and display
function updateVariable() {
    variable += 1; // Increment the variable
    status.textContent = `Variable Value: ${variable}`; // Update display
}

document.addEventListener('keydown', function(e) {
    // For hold mode, start deleting when shift+d is pressed
    if(textWriting)return;
    if ((e.keyCode == 68 || e.key == "d") && e.shiftKey) {
        e.preventDefault();
        // Only activate if this is NOT a repeat event (first press)
        if (!e.repeat) {
            enter_stroke_delete_mode();
        }
    }

});

document.addEventListener('keyup', function(e) {
    // For hold mode, stop deleting when shift+d is released
    if ((e.keyCode == 68 || e.key == "d") && isDeleting) {
        finishDelete()
        exit_stroke_delete_mode();
    }
});
// TODO chinese mode?
// TODO save draw info in cards, no need to save redos
// TODO make clear per side of card by marking which items have been cleared
// TODO add merging of front into back for correct behaviour with saving draw info
// TODO add toggle to not apply front card to the back one
// TODO clear history button?
document.addEventListener('keyup', function(e) {
    // alt + z
    if ((e.keyCode == 90 || e.key == "z") && e.altKey) {
		e.preventDefault();
        ts_undo();
    }
    // alt + y
    if ((e.keyCode == 89 || e.keyCode == "y") && e.altKey) {
        e.preventDefault();
        ts_redo();
    }
    // /
    if (e.key === ".") {
        add_clear_marker();
    }
	// ,
    if (e.key === ",") {
        switch_visibility();
    }
    if ((e.keyCode == 84 || e.key == "t") && e.altKey) {
        e.preventDefault();
        switch_text_writing_mode();
    }
    if ((e.keyCode == 68 || e.key == "d") && e.altKey) {
        e.preventDefault();
        finishDelete()
        switch_stroke_delete_mode();
    }
    // alt + c
    if ((e.keyCode === 67 || e.key === "c") && e.altKey) {
        e.preventDefault();
        switch_calligraphy_mode();
    }
        // alt + x
    if ((e.keyCode === 88 || e.key === "x") && e.altKey) {
        e.preventDefault();
        switch_perfect_freehand();
    }
    // alt + b
    if ((e.keyCode === 66 || e.key === "b") && e.altKey) {
        e.preventDefault();
        switch_small_canvas();
    }
        // alt + 1
    if ((e.keyCode === 49 || e.key === "1") && e.altKey) {
        e.preventDefault();
        activate_pen1();
    }
        // alt + 2
    if ((e.keyCode === 50 || e.key === "2") && e.altKey) {
        e.preventDefault();
        activate_pen2();
    }
        // alt + 3
    if ((e.keyCode === 51 || e.key === "3") && e.altKey) {
        e.preventDefault();
        activate_pen3();
    }
        // alt + 4
    if ((e.keyCode === 52 || e.key === "4") && e.altKey) {
        e.preventDefault();
        activate_pen4();
    }
})

// ----------------------------------------- Stroke Delete -----------------------------------------


function doLinesIntersect(line1, line2) {
    function lineLine(x1, y1, x2, y2, x3, y3, x4, y4) {
        // calculate the distance to intersection point
        var uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));
        var uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));

        // if uA and uB are between 0-1, lines are colliding
        if (uA >= 0 && uA <= 1 && uB >= 0 && uB <= 1) {
            return true;
        }
    return false;
    }
    // Iterate over all points in the two arrays
    for (let i = 0; i < line1.length - 1; i++) {
        for (let j = 0; j < line2.length - 1; j++) {
            if (lineLine(line1[i][0], line1[i][1], line1[i + 1][0], line1[i + 1][1], line2[j][0], line2[j][1], line2[j + 1][0], line2[j + 1][1])) {
                return true; // Lines intersect
            }
        }
    }

    return false; // No intersections
}

function pointerDownStrokeDelete(e) {
    wrapper.classList.add('nopointer');
    if (!e.isPrimary || !strokeDelete) { return; }
    submitCurrentText()
    event.preventDefault();
    // Use solid red for delete mode, not transparent
    var pen = getPenColorAndWidthByIndex(activePenIndex);
    currentAction = {
        points: [],
        color: "rgba(255, 0, 0, 1)",
        width: 4,
        opacity: '1',
        visible: true,
        type: 'D', // 'simple', 'perfect', or 'calligraphy'
    };
    secondary_ctx.strokeStyle = secondary_ctx.fillStyle = currentAction.color;
    secondary_ctx.lineWidth = currentAction.width;

    start_drawing();
};

function pointerMoveStrokeDelete(e) {
    if (!e.isPrimary || !strokeDelete) { return; }
    if(isPointerDown) {
        var mousePos = [e.offsetX, e.offsetY];
        if(currentAction.points.length != 0) {
            if(getDist(mousePos,currentAction.points[currentAction.points.length-1])>=MIN_MOUSE_DIST)
                currentAction.points.push(mousePos);
            secondary_ctx.lineWidth = 4;
            drawCurrentPath();
        } else
            currentAction.points.push(mousePos);
    } 
};

function finishDelete(){
    if (!strokeDelete || !currentAction.points || !currentAction.points.length) { return; }
    stop_drawing();
    var pen = getPenColorAndWidthByIndex(activePenIndex)
    secondary_ctx.strokeStyle = pen[0] // active pen Color;
    secondary_ctx.fillStyle = pen[0] //active pen Color;
    secondary_ctx.lineWidth = pen[1] //active pen Color;
    marked_lines = []
    for (let lineIndex = 0; lineIndex < lineHistory.length; lineIndex++) {
        const element = lineHistory[lineIndex];
        if(!element.points || !element.type == 'D' || !element.visible) continue;
        if(doLinesIntersect(element.points, currentAction.points)){
            element.visible = false;//mark as deleted
            marked_lines.push(lineIndex)//add reference for easy undo
        }
    }
    if(marked_lines.length){
        currentAction.deletedList = marked_lines;//add list of lines which were deleted to the list
        currentAction.type = 'D'
        add_action_to_history(currentAction);
    }
    secondary_ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);//clear the guide line in second canvas
    ts_redraw()
}

function pointerUpStrokeDelete(e) {
    wrapper.classList.remove('nopointer');
    stop_drawing();
    if (!e.isPrimary || !strokeDelete || !currentAction.points || !currentAction.points.length) { return; }
    finishDelete();
};

// ----------------------------------------- Perfect Freehand -----------------------------------------

// The rest of the code gets loaded in from PerfectFreehand.js

function med(A, B) {
  return [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2];
}

// Trim SVG path data so number are each two decimal points. This
// improves SVG exports, and prevents rendering errors on points
// with long decimals.
const TO_FIXED_PRECISION = /(\s?[A-Z]?,?-?[0-9]*\.[0-9]{0,2})(([0-9]|e|-)*)/g;

function getSvgPathFromStroke(points){
  if (!points.length) {
    return "";
  }

  const max = points.length - 1;

  return points
    .reduce(
      (acc, point, i, arr) => {
        if (i === max) {
          acc.push(point, med(point, arr[0]), "L", arr[0], "Z");
        } else {
          acc.push(point, med(point, arr[i + 1]));
        }
        return acc;
      },
      ["M", points[0], "Q"],
    )
    .join(" ")
    .replace(TO_FIXED_PRECISION, "$1");
}

function getFreeDrawSvgPath(inputPoints, width, complete) {
  // Consider changing the options for simulated pressure vs real pressure

  const options = {
    simulatePressure: inputPoints[0][2] > 1,
    size: width,
    thinning: 0.6,
    smoothing: 0.5,
    streamline: 0.5,
    easing: (t) => Math.sin((t * Math.PI) / 2), // https://easings.net/#easeOutSine
    last: complete, // LastCommittedPoint is added on pointerup
  };

  return getSvgPathFromStroke(getStroke(inputPoints, options));
}
/*
 -------------------------------- Caligrapher ------------------------------------------
 Created By: August Toman-Yih
 Git Repository: https://github.com/atomanyih/Calligrapher
*/
/* ------------------------------        script.js        -----------------------------*/

// The rest of the code gets loaded in from Caligrapher.js

//Modified to work with current canvas and board
//share the same canvas with pressure drawing
 /*var canvas = document.getElementById('canvas'),
    width = canvas.width,
    height = canvas.height,
    context = canvas.getContext("2d");
	*/

//FIXME REORGANIZE EBERYTING
//--- constants ---//
RESOLUTION = 4; 
WEIGHT = 15;
MIN_MOUSE_DIST = 5;
SPLIT_THRESHOLD = 8;
SQUARE_SIZE = 300;

function drawCurrentPath() {
    secondary_ctx.beginPath();
    secondary_ctx.moveTo(currentAction.points[0][0],currentAction.points[0][1]);
    for(var i = 1; i<currentAction.points.length; i++) {
        secondary_ctx.lineTo(currentAction.points[i][0],currentAction.points[i][1]);
    } 
    secondary_ctx.stroke();
}

function pointerDownCaligraphy(e) {
    wrapper.classList.add('nopointer');
    if (!e.isPrimary || !calligraphy) { return; }
    event.preventDefault();//don't paint anything when clicking on buttons, especially for undo to work
    var pen = getPenColorAndWidthByIndex(activePenIndex);
    currentAction = {
        points: [],
        color: pen[0],
        width: pen[1],
        opacity: pen[2],
        visible: true,
        type: 'C', // 'simple', 'perfect', or 'calligraphy'
    };
    start_drawing();
};

function pointerMoveCaligraphy(e) {
    if (!e.isPrimary || !calligraphy) { return; }
    if(isPointerDown) {
        var mousePos = [e.offsetX, e.offsetY];
        if(currentAction.points.length != 0) {
            if(getDist(mousePos,currentAction.points[currentAction.points.length-1])>=MIN_MOUSE_DIST)
                currentAction.points.push(mousePos);
            drawCurrentPath();
        } else
            currentAction.points.push(mousePos);
    } 
};

function pointerUpCaligraphy(e) {
    wrapper.classList.remove('nopointer');
    stop_drawing();
    if (!e.isPrimary || !calligraphy || !currentAction.points || !currentAction.points.length) { return; }
    
    add_action_to_history(currentAction)
    secondary_ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);//clear the guide line in second canvas
};
</script>
"""

def custom(*args, **kwargs):
    global ts_state_on
    default = ts_default_review_html(*args, **kwargs)
    if not ts_state_on:
        return default
    output = (
        default +
        blackboard_html() +
        blackboard_css() +
        blackboard_js() +
        "<script>" +
        caligrapher_js +
        perfect_freehand_js+
        "</script>"
    )
    return output
mw.reviewer.revHtml = custom


@slot()
def ts_change_font_settings():
    """
    Open Qt's font dialog and set chosen font.
    """
    global ts_font_family, ts_font_size, ts_font_bold, ts_font_italic
    current_font = QFont()
    current_font.setFamily(ts_font_family)
    current_font.setPointSize(ts_font_size)
    current_font.setBold(ts_font_bold)
    current_font.setItalic(ts_font_italic)
    
    font, ok = QFontDialog.getFont(current_font, mw)
    
    if ok:
        ts_font_family = font.family()
        ts_font_size = font.pointSize()
        ts_font_bold = font.bold()
        ts_font_italic = font.italic()
        
        execute_js(f"fontFamily = '{ts_font_family}';")
        execute_js(f"fontSize = {ts_font_size};")
        execute_js(f"fontBold = {str(ts_font_bold).lower()};")
        execute_js(f"fontItalic = {str(ts_font_italic).lower()};")
        
        execute_js("if (typeof ts_redraw === 'function') { ts_redraw(); }")

@slot()
def ts_change_pen_color(pen_number):
    """
    Open color picker and set chosen color for the specified pen.
    """
    # Get current color from global variable
    current_color = globals()[f"ts_pen{pen_number}_color"]
    qcolor_old = QColor(current_color)
    qcolor = QColorDialog.getColor(qcolor_old)
    
    if qcolor.isValid():
        # Update the global variable
        globals()[f"ts_pen{pen_number}_color"] = qcolor.name()
        
        # Reload the reviewer to apply the new color
        execute_js(f"pen{pen_number}Color = '{qcolor.name()}';")
        execute_js("if (typeof update_pen_settings === 'function') { update_pen_settings(); }")

@slot()
def ts_change_pen_width(pen_number):
    """
    Open width picker and set chosen width for the specified pen.
    """
    # Get current width from global variable
    current_width = globals()[f"ts_pen{pen_number}_width"]
    value, accepted = QInputDialog.getDouble(mw, "AnkiDraw", f"Enter the pen {pen_number} width:", current_width)
    
    if accepted:
        # Update the global variable
        globals()[f"ts_pen{pen_number}_width"] = value
        
        # Reload the reviewer to apply the new width
        execute_js(f"pen{pen_number}Width = '{value}';")
        execute_js("if (typeof update_pen_settings === 'function') { update_pen_settings(); }")

@slot()
def ts_change_pen_opacity(pen_number):
    """
    Open opacity picker and set chosen opacity for the specified pen.
    """
    # Get current opacity from global variable
    current_opacity = globals()[f"ts_pen{pen_number}_opacity"]
    value, accepted = QInputDialog.getDouble(mw, "AnkiDraw", f"Enter the pen {pen_number} opacity (0-1):", current_opacity, 0, 1, 2)
    
    if accepted:
        # Update the global variable
        globals()[f"ts_pen{pen_number}_opacity"] = value
        
        # Reload the reviewer to apply the new opacity
        execute_js(f"pen{pen_number}Opacity = '{value}';")
        execute_js("if (typeof update_pen_settings === 'function') { update_pen_settings(); }")
        execute_js("if (typeof ts_redraw === 'function') { ts_redraw(); }")

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AnkiDraw Toolbar And Canvas")

        self.combo_box = QComboBox()
        self.combo_box.addItem("Top-Left")
        self.combo_box.addItem("Top-Right")
        self.combo_box.addItem("Bottom-Left")
        self.combo_box.addItem("Bottom-Right")

        combo_label = QLabel("Location:")

        range_label = QLabel("Offset:")

        start_range_label = QLabel("X Offset:")
        self.start_spin_box = QSpinBox()
        self.start_spin_box.setRange(0, 1000)

        small_width_label = QLabel("Non-Fullscreen Canvas Width:")
        self.small_width_spin_box = QSpinBox()
        self.small_width_spin_box.setRange(0, 9999)

        small_height_label = QLabel("Non-Fullscreen Canvas Height:")
        self.small_height_spin_box = QSpinBox()
        self.small_height_spin_box.setRange(0, 9999)

        end_range_label = QLabel("Y Offset:")
        self.end_spin_box = QSpinBox()
        self.end_spin_box.setRange(0, 1000)

        range_layout = QVBoxLayout()

        small_height_layout = QHBoxLayout()
        small_height_layout.addWidget(small_height_label)
        small_height_layout.addWidget(self.small_height_spin_box)

        small_width_layout = QHBoxLayout()
        small_width_layout.addWidget(small_width_label)
        small_width_layout.addWidget(self.small_width_spin_box)

        color_layout = QHBoxLayout()
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)

        self.color_label = QLabel("Background color: #FFFFFF00")  # Initial color label

        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_button)

        start_layout = QHBoxLayout()
        start_layout.addWidget(start_range_label)
        start_layout.addWidget(self.start_spin_box)

        end_layout = QHBoxLayout()
        end_layout.addWidget(end_range_label)
        end_layout.addWidget(self.end_spin_box)
        range_layout.addLayout(start_layout)
        range_layout.addLayout(end_layout)
        range_layout.addLayout(small_width_layout)
        range_layout.addLayout(small_height_layout)
        

        checkbox_label2 = QLabel("Orient vertically:")
        self.checkbox2 = QCheckBox()

        checkbox_layout2 = QHBoxLayout()
        checkbox_layout2.addWidget(checkbox_label2)
        checkbox_layout2.addWidget(self.checkbox2)

        accept_button = QPushButton("Accept")
        cancel_button = QPushButton("Cancel")
        reset_button = QPushButton("Default")

        accept_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        reset_button.clicked.connect(self.reset_to_default)

        button_layout = QHBoxLayout()
        button_layout.addWidget(accept_button)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(cancel_button)
        

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(combo_label)
        dialog_layout.addWidget(self.combo_box)
        dialog_layout.addWidget(range_label)
        dialog_layout.addLayout(range_layout)
        dialog_layout.addLayout(checkbox_layout2)
        dialog_layout.addLayout(color_layout)
        dialog_layout.addLayout(button_layout)
        
        self.setLayout(dialog_layout)

    def set_values(self, combo_index, start_value, end_value, checkbox_state2, width, height, background_color):
        self.combo_box.setCurrentIndex(combo_index)
        self.start_spin_box.setValue(start_value)
        self.small_height_spin_box.setValue(height)
        self.small_width_spin_box.setValue(width)
        self.end_spin_box.setValue(end_value)
        self.checkbox2.setChecked(checkbox_state2)
        self.color_label.setText(f"Background color: {background_color}")

    def reset_to_default(self):
        self.combo_box.setCurrentIndex(1)
        self.start_spin_box.setValue(2)
        self.end_spin_box.setValue(2)
        self.small_height_spin_box.setValue(500)
        self.small_width_spin_box.setValue(500)
        self.checkbox2.setChecked(True)
        self.color_label.setText("Background color: #FFFFFF00")  # Reset color label

    def select_color(self):
        color_dialog = QColorDialog()
        qcolor_old = QColor(self.color_label.text()[-9:-2])
        color = color_dialog.getColor(qcolor_old, options=QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self.color_label.setText(f"Background color: {(color.name()+color.name(QColor.NameFormat.HexArgb)[1:3]).upper()}")  # Update color label

@slot()
def ts_change_toolbar_settings():
    global ts_orient_vertical, ts_y_offset, ts_x_offset, ts_location, ts_small_width, ts_small_height, ts_background_color
    
    dialog = CustomDialog()
    dialog.set_values(ts_location, ts_x_offset, ts_y_offset, ts_orient_vertical, ts_small_width, ts_small_height, ts_background_color) 
    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:
        ts_location = dialog.combo_box.currentIndex()
        ts_x_offset = dialog.start_spin_box.value()
        ts_y_offset = dialog.end_spin_box.value()
        ts_small_height = dialog.small_height_spin_box.value()
        ts_background_color = dialog.color_label.text()[-9:]
        ts_small_width = dialog.small_width_spin_box.value()
        ts_orient_vertical = dialog.checkbox2.isChecked()
        ts_switch()
        ts_switch()

@slot()
def ts_change_auto_hide_settings():
    """
    Switch auto hide toolbar setting.
    """
    global ts_auto_hide
    ts_auto_hide = not ts_auto_hide
    ts_switch()
    ts_switch()

@slot()
def ts_change_follow_settings():
    """
    Switch whiteboard follow screen.
    """
    global ts_follow
    ts_follow = not ts_follow
    execute_js("fullscreen_follow = " + str(ts_follow).lower() + ";")
    execute_js("if (typeof resize === 'function') { resize(); }")

@slot()
def ts_change_small_default_settings():
    """
    Switch default small canvas mode setting.
    """
    global ts_default_small_canvas
    ts_default_small_canvas = not ts_default_small_canvas
    ts_switch()
    ts_switch()

@slot()
def ts_change_zen_mode_settings():
    """
    Switch default zen mode setting.
    """
    global ts_zen_mode
    ts_zen_mode = not ts_zen_mode
    ts_switch()
    ts_switch()

@slot()
def ts_change_pressure_sensitivity_settings():
    """
    Switch pressure sensitivity setting.
    """
    global ts_pressure_sensitivity
    ts_pressure_sensitivity = not ts_pressure_sensitivity
    execute_js("pressureSensitivity = " + str(ts_pressure_sensitivity).lower() + ";")
    execute_js("if (typeof resize === 'function') { resize(); }")
    
@slot()
def ts_change_auto_hide_pointer_settings():
    """
    Switch auto hide pointer setting.
    """
    global ts_auto_hide_pointer
    ts_auto_hide_pointer = not ts_auto_hide_pointer
    ts_switch()
    ts_switch()

def checkProfile():
    if not ts_profile_loaded:
        showWarning("No profile loaded. AnkiPenDown may not work correctly.")
        return False
    return True

def ts_on():
    """
    Turn on
    """
    if not checkProfile(): return

    global ts_state_on
    ts_state_on = True
    ts_menu_switch.setChecked(True)
    return True

def ts_off():
    """
    Turn off
    """
    if not checkProfile(): return

    global ts_state_on
    ts_state_on = False
    ts_menu_switch.setChecked(False)
    return True

@slot()
def ts_switch():
    """
    Switch AnkiDraw.
    """
    if ts_state_on:
        ts_off()
    else:
        ts_on()
    # Reload current screen.
    if mw.state == "review":
        mw.moveToState("review")
    elif mw.state == "deckBrowser":
        mw.deckBrowser.refresh()
    elif mw.state == "overview":
        mw.overview.refresh()

def ts_setup_menu():
    """
    Initialize menu. 
    """
    global ts_menu_switch, ts_menu_auto_hide, ts_menu_auto_hide_pointer, ts_menu_small_default, ts_menu_zen_mode, ts_menu_follow, ts_menu_pressure

    try:
        mw.addon_view_menu
    except AttributeError:
        mw.addon_view_menu = QMenu("""&AnkiDraw""", mw)
        mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(),
                                    mw.addon_view_menu)

    # mw.ts_menu = QMenu(_('&AnkiDraw'), mw)

    # mw.addon_view_menu.addMenu(mw.ts_menu)

    ts_menu_switch = QAction("""&Enable Ankidraw""", mw, checkable=True)
    ts_menu_pressure = QAction("""Enable &pressure sensitivity""", mw, checkable=True)
    ts_menu_auto_hide = QAction("""Auto &hide toolbar when drawing""", mw, checkable=True)
    ts_menu_auto_hide_pointer = QAction("""Auto &hide pointer when drawing""", mw, checkable=True)
    ts_menu_follow = QAction("""&Follow when scrolling (speedup draw)""", mw, checkable=True)
    ts_menu_small_default = QAction("""&Small Canvas by default (speedup draw)""", mw, checkable=True)
    ts_menu_zen_mode = QAction("""Enable Zen Mode(hide toolbar until disabled)""", mw, checkable=True)
    ts_toolbar_settings = QAction("""&Toolbar and canvas location settings""", mw)
    ts_font_settings = QAction("""Select &Font for text writing""", mw)    

    ts_toggle_seq = QKeySequence("Ctrl+r")
    ts_menu_switch.setShortcut(ts_toggle_seq)

    ts_pen_color_menu = QMenu("Set pen 1-4 color", mw)
    ts_menu_pen1_color = QAction("Set Pen 1 Color", mw)
    ts_menu_pen2_color = QAction("Set Pen 2 Color", mw)
    ts_menu_pen3_color = QAction("Set Pen 3 Color", mw)
    ts_menu_pen4_color = QAction("Set Pen 4 Color", mw)
    ts_pen_color_menu.addAction(ts_menu_pen1_color)
    ts_pen_color_menu.addAction(ts_menu_pen2_color)
    ts_pen_color_menu.addAction(ts_menu_pen3_color)
    ts_pen_color_menu.addAction(ts_menu_pen4_color)

    ts_pen_width_menu = QMenu("Set pen 1-4 width", mw)
    ts_menu_pen1_width = QAction("Set Pen 1 width", mw)
    ts_menu_pen2_width = QAction("Set Pen 2 width", mw)
    ts_menu_pen3_width = QAction("Set Pen 3 width", mw)
    ts_menu_pen4_width = QAction("Set Pen 4 width", mw)
    ts_pen_width_menu.addAction(ts_menu_pen1_width)
    ts_pen_width_menu.addAction(ts_menu_pen2_width)
    ts_pen_width_menu.addAction(ts_menu_pen3_width)
    ts_pen_width_menu.addAction(ts_menu_pen4_width)

    ts_pen_opacity_menu = QMenu("Set pen 1-4 opacity", mw)
    ts_menu_pen1_opacity = QAction("Set Pen 1 Opacity", mw)
    ts_menu_pen2_opacity = QAction("Set Pen 2 Opacity", mw)
    ts_menu_pen3_opacity = QAction("Set Pen 3 Opacity", mw)
    ts_menu_pen4_opacity = QAction("Set Pen 4 Opacity", mw)
    ts_pen_opacity_menu.addAction(ts_menu_pen1_opacity)
    ts_pen_opacity_menu.addAction(ts_menu_pen2_opacity)
    ts_pen_opacity_menu.addAction(ts_menu_pen3_opacity)
    ts_pen_opacity_menu.addAction(ts_menu_pen4_opacity)

    mw.addon_view_menu.addAction(ts_menu_switch)
    mw.addon_view_menu.addAction(ts_menu_pressure)
    mw.addon_view_menu.addAction(ts_menu_auto_hide)
    mw.addon_view_menu.addAction(ts_menu_auto_hide_pointer)
    mw.addon_view_menu.addAction(ts_menu_follow)
    mw.addon_view_menu.addAction(ts_menu_small_default)
    mw.addon_view_menu.addAction(ts_menu_zen_mode)
    mw.addon_view_menu.addMenu(ts_pen_color_menu)
    mw.addon_view_menu.addMenu(ts_pen_width_menu)
    mw.addon_view_menu.addMenu(ts_pen_opacity_menu)
    mw.addon_view_menu.addAction(ts_toolbar_settings)
    mw.addon_view_menu.addAction(ts_font_settings)

    ts_menu_pen1_color.triggered.connect(lambda: ts_change_pen_color(1))
    ts_menu_pen2_color.triggered.connect(lambda: ts_change_pen_color(2))
    ts_menu_pen3_color.triggered.connect(lambda: ts_change_pen_color(3))
    ts_menu_pen4_color.triggered.connect(lambda: ts_change_pen_color(4))
    ts_menu_pen1_width.triggered.connect(lambda: ts_change_pen_width(1))
    ts_menu_pen2_width.triggered.connect(lambda: ts_change_pen_width(2))
    ts_menu_pen3_width.triggered.connect(lambda: ts_change_pen_width(3))
    ts_menu_pen4_width.triggered.connect(lambda: ts_change_pen_width(4))
    ts_menu_pen1_opacity.triggered.connect(lambda: ts_change_pen_opacity(1))
    ts_menu_pen2_opacity.triggered.connect(lambda: ts_change_pen_opacity(2))
    ts_menu_pen3_opacity.triggered.connect(lambda: ts_change_pen_opacity(3))
    ts_menu_pen4_opacity.triggered.connect(lambda: ts_change_pen_opacity(4))
    ts_menu_switch.triggered.connect(ts_switch)
    ts_menu_pressure.triggered.connect(ts_change_pressure_sensitivity_settings)
    ts_menu_auto_hide.triggered.connect(ts_change_auto_hide_settings)
    ts_menu_auto_hide_pointer.triggered.connect(ts_change_auto_hide_pointer_settings)
    ts_menu_follow.triggered.connect(ts_change_follow_settings)
    ts_menu_small_default.triggered.connect(ts_change_small_default_settings)
    ts_menu_zen_mode.triggered.connect(ts_change_zen_mode_settings)
    ts_toolbar_settings.triggered.connect(ts_change_toolbar_settings)
    ts_font_settings.triggered.connect(ts_change_font_settings)

#
# ONLOAD SECTION
#
def ts_onload():
    """
    Add hooks and initialize menu.
    Call to this function is placed on the end of this file.
    """
    addHook("unloadProfile", ts_save)
    addHook("profileLoaded", ts_load)
    addHook("showQuestion", clear_blackboard)
    addHook("showAnswer", resize_js)
    ts_setup_menu()

ts_onload()

from aqt.qt import QTimer

def apply_visibility_logic():
    """
    Checks for the 'draw' tag and directly calls the
    appropriate JavaScript function to show or hide the canvas.
    """
    if not mw.reviewer.card or not mw.reviewer.web:
        return

    target_tag = "draw" 

    note_tags = [t.lower() for t in mw.reviewer.card.note().tags]
    should_show = target_tag.lower() in note_tags

    if should_show:
        mw.reviewer.web.eval("forceShowCanvas();")
    else:
        mw.reviewer.web.eval("forceHideCanvas();")

def check_for_draw_tag_wrapper(*args):
    """
    Wrapper to handle hook arguments and add a small delay
    to ensure the card's web content is fully loaded.
    """
    QTimer.singleShot(100, apply_visibility_logic)

addHook("showQuestion", check_for_draw_tag_wrapper)