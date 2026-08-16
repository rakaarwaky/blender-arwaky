# bpy.types.UILayout

# UILayout(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.UILayout(bpy_struct) 

User interface layout in a panel or header

   activate_init 

When true, buttons defined in popups will be activated on first display (use so you can type into a field without having to click on it first) (default False)

  Type: 

bool

      active 

(default False)

  Type: 

bool

      active_default 

When true, an operator button defined after this will be activated when pressing return(use with popup dialogs) (default False)

  Type: 

bool

      alert 

(default False)

  Type: 

bool

      alignment 

(default `'EXPAND'`)

  Type: 

Literal[‘EXPAND’, ‘LEFT’, ‘CENTER’, ‘RIGHT’]

      direction 

(default `'HORIZONTAL'`, readonly)

  Type: 

Literal[‘HORIZONTAL’, ‘VERTICAL’]

      emboss 

(default `'NORMAL'`)

  
- `NORMAL` Regular – Draw standard button emboss style. 
- `NONE` None – Draw only text and icons. 
- `PULLDOWN_MENU` Pull-down Menu – Draw pull-down menu style. 
- `PIE_MENU` Pie Menu – Draw radial menu style. 
- `NONE_OR_STATUS` None or Status – Draw with no emboss unless the button has a coloring status like an animation state.   Type: 

Literal[‘NORMAL’, ‘NONE’, ‘PULLDOWN_MENU’, ‘PIE_MENU’, ‘NONE_OR_STATUS’]

      enabled 

When false, this (sub)layout is grayed out (default False)

  Type: 

bool

      operator_context 

Typically set to ‘INVOKE_REGION_WIN’, except some cases in [`bpy.types.Menu`](bpy.types.Menu.html#bpy.types.Menu) when it’s set to ‘EXEC_REGION_WIN’. (default `'INVOKE_DEFAULT'`)

  Type: 

Literal[[Operator Context Items](bpy_types_enum_items/operator_context_items.html#rna-enum-operator-context-items)]

      scale_x 

Scale factor along the X for items in this (sub)layout (in [0, inf], default 0.0)

  Type: 

float

      scale_y 

Scale factor along the Y for items in this (sub)layout (in [0, inf], default 0.0)

  Type: 

float

      ui_units_x 

Fixed size along the X for items in this (sub)layout (in [0, inf], default 0.0)

  Type: 

float

      ui_units_y 

Fixed size along the Y for items in this (sub)layout (in [0, inf], default 0.0)

  Type: 

float

      use_property_decorate 

(default False)

  Type: 

bool

      use_property_split 

(default False)

  Type: 

bool

      row(*, align=False, heading='', heading_ctxt='', translate=True) 

Sub-layout. Items placed in this sublayout are placed next to each other in a row.

  Parameters:  
- align (bool) – Align buttons to each other (optional) 
- heading (str) – Heading, Label to insert into the layout for this sub-layout (optional, never None) 
- heading_ctxt (str) – Override automatic translation context of the given heading (optional, never None) 
- translate (bool) – Translate the given heading, when UI translation is enabled (optional)   Returns: 

Sub-layout to put items in

  Return type: 

`UILayout`

      column(*, align=False, heading='', heading_ctxt='', translate=True) 

Sub-layout. Items placed in this sublayout are placed under each other in a column.

  Parameters:  
- align (bool) – Align buttons to each other (optional) 
- heading (str) – Heading, Label to insert into the layout for this sub-layout (optional, never None) 
- heading_ctxt (str) – Override automatic translation context of the given heading (optional, never None) 
- translate (bool) – Translate the given heading, when UI translation is enabled (optional)   Returns: 

Sub-layout to put items in

  Return type: 

`UILayout`

      panel(idname, *, default_closed=False) 

Creates a collapsible panel. Whether it is open or closed is stored in the region using the given idname. This can only be used when the panel has the full width of the panel region available to it. So it can’t be used in e.g. in a box or columns.

  Parameters:  
- idname (str) – Identifier of the panel (never None) 
- default_closed (bool) – Open by Default, When true, the panel will be open the first time it is shown (optional)   Returns: 

`layout_header`, Sub-layout to put items in, `UILayout`

 

`layout_body`, Sub-layout to put items in. Will be none if the panel is collapsed., `UILayout`

  Return type: 

tuple[`UILayout`, `UILayout`]

      panel_prop(data, property) 

Similar to `.panel(...)` but instead of storing whether it is open or closed in the region, it is stored in the provided boolean property. This should be used when multiple instances of the same panel can exist. For example one for every item in a collection property or list. This can only be used when the panel has the full width of the panel region available to it. So it can’t be used in e.g. in a box or columns.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take the open-state property (never None) 
- property (str) – Identifier of the boolean property that determines whether the panel is open or closed (never None)   Returns: 

`layout_header`, Sub-layout to put items in, `UILayout`

 

`layout_body`, Sub-layout to put items in. Will be none if the panel is collapsed., `UILayout`

  Return type: 

tuple[`UILayout`, `UILayout`]

      column_flow(*, columns=0, align=False) 

column_flow

  Parameters:  
- columns (int) – Number of columns, 0 is automatic (in [0, inf], optional) 
- align (bool) – Align buttons to each other (optional)   Returns: 

Sub-layout to put items in

  Return type: 

`UILayout`

      grid_flow(*, row_major=False, columns=0, even_columns=False, even_rows=False, align=False) 

grid_flow

  Parameters:  
- row_major (bool) – Fill row by row, instead of column by column (optional) 
- columns (int) – Number of columns, positive are absolute fixed numbers, 0 is automatic, negative are automatic multiple numbers along major axis (e.g. -2 will only produce 2, 4, 6 etc. columns for row major layout, and 2, 4, 6 etc. rows for column major layout). (in [-inf, inf], optional) 
- even_columns (bool) – All columns will have the same width (optional) 
- even_rows (bool) – All rows will have the same height (optional) 
- align (bool) – Align buttons to each other (optional)   Returns: 

Sub-layout to put items in

  Return type: 

`UILayout`

      box() 

Sublayout (items placed in this sublayout are placed under each other in a column and are surrounded by a box)

  Returns: 

Sub-layout to put items in

  Return type: 

`UILayout`

      split(*, factor=0.0, align=False) 

split

  Parameters:  
- factor (float) – Percentage, Percentage of width to split at (leave unset for automatic calculation) (in [0, 1], optional) 
- align (bool) – Align buttons to each other (optional)   Returns: 

Sub-layout to put items in

  Return type: 

`UILayout`

      menu_pie() 

Sublayout. Items placed in this sublayout are placed in a radial fashion around the menu center).

  Returns: 

Sub-layout to put items in

  Return type: 

`UILayout`

      classmethod icon(data) 

Return the custom icon for this data, use it e.g. to get materials or texture icons.

  Parameters: 

data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take the icon (never None)

  Returns: 

Icon identifier (in [0, inf])

  Return type: 

int

      classmethod enum_item_name(data, property, identifier) 

Return the UI name for this enum item

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- identifier (str) – Identifier of the enum item (never None)   Returns: 

UI name of the enum item (never None)

  Return type: 

str

      classmethod enum_item_description(data, property, identifier) 

Return the UI description for this enum item

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- identifier (str) – Identifier of the enum item (never None)   Returns: 

UI description of the enum item (never None)

  Return type: 

str

      classmethod enum_item_icon(data, property, identifier) 

Return the icon for this enum item

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- identifier (str) – Identifier of the enum item (never None)   Returns: 

Icon identifier (in [0, inf])

  Return type: 

int

      textbox(data, property, *, initial_visible_lines=3, placeholder='', text_ctxt='', translate=True) 

Exposes an RNA string property in the layout using a text-box widget with multi-line support. Text-box state will be stored in the current context region.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- initial_visible_lines (int) – Initial Visible Lines, (in [1, inf], optional) 
- placeholder (str) – Hint describing the expected value when empty (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       textbox_with_state(data, property, textbox_state, *, placeholder='', text_ctxt='', translate=True) 

Exposes an RNA string property in the layout using a text-box widget with multi-line support

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- textbox_state ([`TextboxState`](bpy.types.TextboxState.html#bpy.types.TextboxState) | None) – Pointer to a pre-allocated text-box state storage (builtin) (never None) 
- placeholder (str) – Hint describing the expected value when empty (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       prop(data, property, *, text='', text_ctxt='', translate=True, icon='NONE', placeholder='', expand=False, slider=False, toggle=-1, icon_only=False, event=False, full_event=False, emboss=True, index=-1, icon_value=0, invert_checkbox=False, text_align='LEFT') 

Item. Exposes an RNA item and places it into the layout.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- placeholder (str) – Hint describing the expected value when empty (optional) 
- expand (bool) – Expand button to show more detail (optional) 
- slider (bool) – Use slider widget for numeric values (optional) 
- toggle (int) – Use toggle widget for boolean values, or a checkbox when disabled (the default is -1 which uses toggle only when an icon is displayed) (in [-1, 1], optional) 
- icon_only (bool) – Draw only icons in buttons, no text (optional) 
- event (bool) – Use button to input key events (optional) 
- full_event (bool) – Use button to input full events including modifiers (optional) 
- emboss (bool) – Draw the button itself, not just the icon/text. When false, corresponds to the ‘NONE_OR_STATUS’ layout emboss type. (optional) 
- index (int) – The index of this button, when set a single member of an array can be accessed, when set to -1 all array members are used (in [-2, inf], optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional) 
- invert_checkbox (bool) – Draw checkbox value inverted (optional) 
- text_align (Literal['LEFT', 'RIGHT']) – Text alignment (optional)       props_enum(data, property) 

props_enum

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       prop_menu_enum(data, property, *, text='', text_ctxt='', translate=True, icon='NONE') 

prop_menu_enum

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional)       prop_with_popover(data, property, *, text='', text_ctxt='', translate=True, icon='NONE', icon_only=False, panel) 

prop_with_popover

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- icon_only (bool) – Draw only icons in tabs, no text (optional) 
- panel (str) – Identifier of the panel (never None)       prop_with_menu(data, property, *, text='', text_ctxt='', translate=True, icon='NONE', icon_only=False, menu) 

prop_with_menu

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- icon_only (bool) – Draw only icons in tabs, no text (optional) 
- menu (str) – Identifier of the menu (never None)       prop_tabs_enum(data, property, *, data_highlight=None, property_highlight='', icon_only=False, expand_as='DEFAULT') 

prop_tabs_enum

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- data_highlight ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take highlight property (optional, never None) 
- property_highlight (str) – Identifier of highlight property in data (optional, never None) 
- icon_only (bool) – Draw only icons in tabs, no text (optional) 
- expand_as (Literal['DEFAULT', 'ROW']) – (optional)       prop_enum(data, property, value, *, text='', text_ctxt='', translate=True, icon='NONE') 

prop_enum

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- value (str) – Enum property value (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional)       prop_search(data, property, search_data, search_property, *, text='', text_ctxt='', translate=True, icon='NONE', results_are_suggestions=False, item_search_property='') 

prop_search

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- search_data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take collection to search in (never None) 
- search_property (str) – Identifier of search collection property (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- results_are_suggestions (bool) – Accept inputs that do not match any item (optional) 
- item_search_property (str) – Identifier of the string property in each collection’s items to use for searching (defaults to the items’ type ‘name property’) (optional, never None)       prop_decorator(data, property, *, index=-1) 

prop_decorator

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- index (int) – The index of this button, when set a single member of an array can be accessed, when set to -1 all array members are used (in [-2, inf], optional)       operator(operator, *, text='', text_ctxt='', translate=True, icon='NONE', emboss=True, depress=False, icon_value=0, search_weight=0.0) 

Item. Places a button into the layout to call an Operator.

  Parameters:  
- operator (str) – Identifier of the operator (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- emboss (bool) – Draw the button itself, not just the icon/text (optional) 
- depress (bool) – Draw pressed in (optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional) 
- search_weight (float) – Search Weight, Influences the sorting when using menu-seach (in [-inf, inf], optional)   Returns: 

Operator properties to fill in

  Return type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties)

      operator_menu_hold(operator, *, text='', text_ctxt='', translate=True, icon='NONE', emboss=True, depress=False, icon_value=0, menu) 

Item. Places a button into the layout to call an Operator.

  Parameters:  
- operator (str) – Identifier of the operator (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- emboss (bool) – Draw the button itself, not just the icon/text (optional) 
- depress (bool) – Draw pressed in (optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional) 
- menu (str) – Identifier of the menu (never None)   Returns: 

Operator properties to fill in

  Return type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties)

      operator_enum(operator, property, *, icon_only=False) 

operator_enum

  Parameters:  
- operator (str) – Identifier of the operator (never None) 
- property (str) – Identifier of property in operator (never None) 
- icon_only (bool) – Draw only icons in buttons, no text (optional)       operator_menu_enum(operator, property, *, text='', text_ctxt='', translate=True, icon='NONE') 

operator_menu_enum

  Parameters:  
- operator (str) – Identifier of the operator (never None) 
- property (str) – Identifier of property in operator (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional)   Returns: 

Operator properties to fill in

  Return type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties)

      label(*, text='', text_ctxt='', translate=True, icon='NONE', icon_value=0) 

Item. Displays text and/or icon in the layout.

  Parameters:  
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional)       link(*, url='', text='', text_ctxt='', translate=True, icon='NONE', icon_value=0) 

Item. Displays a url that can be clicked in the layout.

  Parameters:  
- url (str) – (optional, never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional)       menu(menu, *, text='', text_ctxt='', translate=True, icon='NONE', icon_value=0) 

menu

  Parameters:  
- menu (str) – Identifier of the menu (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional)       menu_contents(menu) 

menu_contents

  Parameters: 

menu (str) – Identifier of the menu (never None)

      popover(panel, *, text='', text_ctxt='', translate=True, icon='NONE', icon_value=0, direction='VERTICAL') 

popover

  Parameters:  
- panel (str) – Identifier of the panel (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional) 
- direction (Literal['VERTICAL', 'HORIZONTAL']) – 

Popup Direction, The direction in which the popup panel is drawn relative to button position (optional)

  
- `VERTICAL` Vertical – Draw popup panel above or below the button. 
- `HORIZONTAL` Horizontal – Draw popup panel to the side of the button.       popover_group(space_type, region_type, context, category) 

popover_group

  Parameters:  
- space_type (Literal[[Space Type Items](bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items)]) – Space Type 
- region_type (Literal[[Region Type Items](bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items)]) – Region Type 
- context (str) – panel type context (never None) 
- category (str) – panel type category (never None)       separator(*, factor=1.0, type='AUTO') 

Item. Inserts empty space into the layout between items.

  Parameters:  
- factor (float) – Percentage, Percentage of width to space (leave unset for default space) (in [0, inf], optional) 
- type (Literal['AUTO', 'SPACE', 'LINE']) – 

Type, The type of the separator (optional)

  
- `AUTO` Auto – Best guess at what type of separator is needed.. 
- `SPACE` Empty space – Horizontal or Vertical empty space, depending on layout direction.. 
- `LINE` Line – Horizontal or Vertical line, depending on layout direction..       separator_spacer() 

Item. Inserts horizontal spacing empty space into the layout between items.

    progress(*, text='', text_ctxt='', translate=True, factor=0.0, type='BAR') 

Progress indicator

  Parameters:  
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- factor (float) – Factor, Amount of progress from 0.0f to 1.0f (in [0, 1], optional) 
- type (Literal['BAR', 'RING']) – Type, The type of progress indicator (optional)       context_pointer_set(name, data) 

context_pointer_set

  Parameters:  
- name (str) – Name, Name of entry in the context (never None) 
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Pointer to put in context       context_string_set(name, value) 

context_string_set

  Parameters:  
- name (str) – Name, Name of entry in the context (never None) 
- value (str) – Value, String to put in context (never None)       template_header() 

Inserts common Space header UI (editor type selector)

    template_ID(data, property, *, new='', open='', unlink='', filter='ALL', live_icon=False, text='', text_ctxt='', translate=True) 

template_ID

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- new (str) – Operator identifier to create a new ID block (optional, never None) 
- open (str) – Operator identifier to open a file for creating a new ID block (optional, never None) 
- unlink (str) – Operator identifier to unlink the ID block (optional, never None) 
- filter (Literal['ALL', 'AVAILABLE']) – Optionally limit the items which can be selected (optional) 
- live_icon (bool) – Show preview instead of fixed icon (optional) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       template_ID_session_uid(data, property, id_type) 

Template ID search menu button for session_uid Int properties

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- id_type (Literal[[Id Type Items](bpy_types_enum_items/id_type_items.html#rna-enum-id-type-items)]) – Type of ID to display in the search list       template_ID_preview(data, property, *, new='', open='', unlink='', rows=0, cols=0, filter='ALL', hide_buttons=False) 

template_ID_preview

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- new (str) – Operator identifier to create a new ID block (optional, never None) 
- open (str) – Operator identifier to open a file for creating a new ID block (optional, never None) 
- unlink (str) – Operator identifier to unlink the ID block (optional, never None) 
- rows (int) – Number of thumbnail preview rows to display, (in [0, inf], optional) 
- cols (int) – Number of thumbnail preview columns to display, (in [0, inf], optional) 
- filter (Literal['ALL', 'AVAILABLE']) – Optionally limit the items which can be selected (optional) 
- hide_buttons (bool) – Show only list, no buttons (optional)       template_matrix(data, property) 

Insert a readonly Matrix UI. The UI displays the matrix components - translation, rotation and scale. The property argument must be the identifier of an existing 4x4 float vector property of subtype ‘MATRIX’.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_any_ID(data, property, type_property, *, text='', text_ctxt='', translate=True) 

template_any_ID

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- type_property (str) – Identifier of property in data giving the type of the ID-blocks to use (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       template_ID_tabs(data, property, *, new='', menu='', filter='ALL') 

template_ID_tabs

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- new (str) – Operator identifier to create a new ID block (optional, never None) 
- menu (str) – Context menu identifier (optional, never None) 
- filter (Literal['ALL', 'AVAILABLE']) – Optionally limit the items which can be selected (optional)       template_action(id, *, new='', unlink='', text='', text_ctxt='', translate=True) 

template_action

  Parameters:  
- id ([`ID`](bpy.types.ID.html#bpy.types.ID) | None) – The data-block for which to select an Action (never None) 
- new (str) – Operator identifier to create a new ID block (optional, never None) 
- unlink (str) – Operator identifier to unlink the ID block (optional, never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       template_search(data, property, search_data, search_property, *, new='', unlink='', text='', text_ctxt='', translate=True) 

template_search

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- search_data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take collection to search in (never None) 
- search_property (str) – Identifier of search collection property (never None) 
- new (str) – Operator identifier to create a new item for the collection (optional, never None) 
- unlink (str) – Operator identifier to unlink or delete the active item from the collection (optional, never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       template_search_preview(data, property, search_data, search_property, *, new='', unlink='', text='', text_ctxt='', translate=True, rows=0, cols=0) 

template_search_preview

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- search_data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take collection to search in (never None) 
- search_property (str) – Identifier of search collection property (never None) 
- new (str) – Operator identifier to create a new item for the collection (optional, never None) 
- unlink (str) – Operator identifier to unlink or delete the active item from the collection (optional, never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- rows (int) – Number of thumbnail preview rows to display, (in [0, inf], optional) 
- cols (int) – Number of thumbnail preview columns to display, (in [0, inf], optional)       template_path_builder(data, property, root, *, text='', text_ctxt='', translate=True) 

template_path_builder

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- root ([`ID`](bpy.types.ID.html#bpy.types.ID) | None) – ID-block from which path is evaluated from 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       template_modifiers() 

Generates the UI layout for the modifier stack

    template_strip_modifiers() 

Generates the UI layout for the strip modifier stack

    template_collection_importer() 

Generates the UI layout for the collection importer

    template_collection_exporters() 

Generates the UI layout for collection exporters

    template_constraints(*, use_bone_constraints=True) 

Generates the panels for the constraint stack

  Parameters: 

use_bone_constraints (bool) – Add panels for bone constraints instead of object constraints (optional)

      template_shaderfx() 

Generates the panels for the shader effect stack

    template_greasepencil_color(data, property, *, rows=0, cols=0, scale=1.0, filter='ALL') 

template_greasepencil_color

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- rows (int) – Number of thumbnail preview rows to display, (in [0, inf], optional) 
- cols (int) – Number of thumbnail preview columns to display, (in [0, inf], optional) 
- scale (float) – Scale of the image thumbnails, (in [0.1, 1.5], optional) 
- filter (Literal['ALL', 'AVAILABLE']) – Optionally limit the items which can be selected (optional)       template_constraint_header(data) 

Generates the header for constraint panels

  Parameters: 

data ([`Constraint`](bpy.types.Constraint.html#bpy.types.Constraint) | None) – Constraint data (never None)

      template_preview(id, *, show_buttons=True, parent=None, slot=None, preview_id='') 

Item. A preview window for materials, textures, lights or worlds.

  Parameters:  
- id ([`ID`](bpy.types.ID.html#bpy.types.ID) | None) – ID data-block 
- show_buttons (bool) – Show preview buttons? (optional) 
- parent ([`ID`](bpy.types.ID.html#bpy.types.ID) | None) – ID data-block (optional) 
- slot ([`TextureSlot`](bpy.types.TextureSlot.html#bpy.types.TextureSlot) | None) – Texture slot (optional) 
- preview_id (str) – Identifier of this preview widget, if not set the ID type will be used (i.e. all previews of materials without explicit ID will have the same size…). (optional, never None)       template_curve_mapping(data, property, *, type='NONE', levels=False, brush=False, use_negative_slope=False, show_tone=False, show_presets=False) 

Item. A curve mapping widget used for e.g falloff curves for lights.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- type (Literal['NONE', 'VECTOR', 'COLOR', 'HUE']) – Type, Type of curves to display (optional) 
- levels (bool) – Show black/white levels (optional) 
- brush (bool) – Show brush options (optional) 
- use_negative_slope (bool) – Use a negative slope by default (optional) 
- show_tone (bool) – Show tone options (optional) 
- show_presets (bool) – Show preset options (optional)       template_curveprofile(data, property) 

A profile path editor used for custom profiles

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_color_ramp(data, property, *, expand=False) 

Item. A color ramp widget.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- expand (bool) – Expand button to show more detail (optional)       template_icon(icon_value, *, scale=1.0) 

Display a large icon

  Parameters:  
- icon_value (int) – Icon to display, (in [0, inf]) 
- scale (float) – Scale, Scale the icon size (by the button size) (in [1, 100], optional)       template_icon_view(data, property, *, show_labels=False, scale=6.0, scale_popup=5.0) 

Enum. Large widget showing Icon previews.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- show_labels (bool) – Show enum label in preview buttons (optional) 
- scale (float) – UI Units, Scale the button icon size (by the button size) (in [1, 100], optional) 
- scale_popup (float) – Scale, Scale the popup icon size (by the button size) (in [1, 100], optional)       template_histogram(data, property) 

Item. A histogramm widget to analyze imaga data.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_waveform(data, property) 

Item. A waveform widget to analyze imaga data.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_vectorscope(data, property) 

Item. A vectorscope widget to analyze imaga data.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_layers(data, property, used_layers_data, used_layers_property, active_layer) 

template_layers

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- used_layers_data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property 
- used_layers_property (str) – Identifier of property in data (never None) 
- active_layer (int) – Active Layer, (in [0, inf])       template_color_picker(data, property, *, value_slider=False, lock=False, lock_luminosity=False, cubic=False) 

Item. A color wheel widget to pick colors.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- value_slider (bool) – Display the value slider to the right of the color wheel (optional) 
- lock (bool) – Lock the color wheel display to value 1.0 regardless of actual color (optional) 
- lock_luminosity (bool) – Keep the color at its original vector length (optional) 
- cubic (bool) – Cubic saturation for picking values close to white (optional)       template_palette(data, property) 

Item. A palette used to pick colors.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_image_layers(image, image_user) 

template_image_layers

  Parameters:  
- image ([`Image`](bpy.types.Image.html#bpy.types.Image) | None) – Image data-block to display layers for 
- image_user ([`ImageUser`](bpy.types.ImageUser.html#bpy.types.ImageUser) | None) – Image user reading from the image       template_image(data, property, image_user, *, compact=False, multiview=False) 

Item(s). User interface for selecting images and their source paths.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- image_user ([`ImageUser`](bpy.types.ImageUser.html#bpy.types.ImageUser) | None) – (never None) 
- compact (bool) – Use more compact layout (optional) 
- multiview (bool) – Expose Multi-View options (optional)       template_image_settings(image_settings, *, color_management=False) 

User interface for setting image format options

  Parameters:  
- image_settings ([`ImageFormatSettings`](bpy.types.ImageFormatSettings.html#bpy.types.ImageFormatSettings) | None) – (never None) 
- color_management (bool) – Show color management settings (optional)       template_image_stereo_3d(stereo_3d_format) 

User interface for setting image stereo 3d options

  Parameters: 

stereo_3d_format ([`Stereo3dFormat`](bpy.types.Stereo3dFormat.html#bpy.types.Stereo3dFormat) | None) – (never None)

      template_image_views(image_settings) 

User interface for setting image views output options

  Parameters: 

image_settings ([`ImageFormatSettings`](bpy.types.ImageFormatSettings.html#bpy.types.ImageFormatSettings) | None) – (never None)

      template_movieclip(data, property, *, compact=False) 

Item(s). User interface for selecting movie clips and their source paths.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- compact (bool) – Use more compact layout (optional)       template_track(data, property) 

Item. A movie-track widget to preview tracking image.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_marker(data, property, clip_user, track, *, compact=False) 

Item. A widget to control single marker settings.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- clip_user ([`MovieClipUser`](bpy.types.MovieClipUser.html#bpy.types.MovieClipUser) | None) – (never None) 
- track ([`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.html#bpy.types.MovieTrackingTrack) | None) – (never None) 
- compact (bool) – Use more compact layout (optional)       template_movieclip_information(data, property, clip_user) 

Item. Movie clip information data.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- clip_user ([`MovieClipUser`](bpy.types.MovieClipUser.html#bpy.types.MovieClipUser) | None) – (never None)       template_list(listtype_name, list_id, dataptr, propname, active_dataptr, active_propname, *, item_dyntip_propname='', rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False) 

Item. A list widget to display data, e.g. vertexgroups.

  Parameters:  
- listtype_name (str) – Identifier of the list type to use (never None) 
- list_id (str) – Identifier of this list widget. Necessary to tell apart different list widgets. Mandatory when using default “UI_UL_list” class. If this not an empty string, the uilist gets a custom ID, otherwise it takes the name of the class used to define the uilist (for example, if the class name is “OBJECT_UL_vgroups”, and list_id is not set by the script, then bl_idname = “OBJECT_UL_vgroups”) (never None) 
- dataptr ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take the Collection property 
- propname (str) – Identifier of the Collection property in data (never None) 
- active_dataptr ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take the integer property, index of the active item (never None) 
- active_propname (str) – Identifier of the integer property in active_data, index of the active item (never None) 
- item_dyntip_propname (str) – Identifier of a string property in items, to use as tooltip content (optional, never None) 
- rows (int) – Default and minimum number of rows to display (in [0, inf], optional) 
- maxrows (int) – Default maximum number of rows to display (in [0, inf], optional) 
- type (Literal[[Uilist Layout Type Items](bpy_types_enum_items/uilist_layout_type_items.html#rna-enum-uilist-layout-type-items)]) – Type, Type of layout to use (optional) 
- columns (int) – Number of items to display per row, for GRID layout (in [0, inf], optional) 
- sort_reverse (bool) – Display items in reverse order by default (optional) 
- sort_lock (bool) – Lock display order to default value (optional)       template_running_jobs() 

template_running_jobs

    template_operator_search() 

template_operator_search

    template_menu_search() 

template_menu_search

    template_header_3D_mode()    template_edit_mode_selection() 

Inserts common 3DView Edit modes header UI (selector for selection mode)

    template_reports_banner() 

template_reports_banner

    template_input_status() 

template_input_status

    template_status_info() 

template_status_info

    template_node_link(ntree, node, socket) 

template_node_link

  Parameters:  
- ntree ([`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree) | None) – Node tree containing the node 
- node ([`Node`](bpy.types.Node.html#bpy.types.Node) | None) – Node owning the socket 
- socket ([`NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket) | None) – Socket to display the link for       template_node_view(ntree, node, socket) 

template_node_view

  Parameters:  
- ntree ([`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree) | None) – Node tree containing the node 
- node ([`Node`](bpy.types.Node.html#bpy.types.Node) | None) – Node to display 
- socket ([`NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket) | None) – Socket to display       template_node_operator_registration_errors(*, idname='') 

template_node_operator_registration_errors

  Parameters: 

idname (str) – (optional, never None)

      template_node_asset_menu_items(*, catalog_path='', operator='ADD') 

template_node_asset_menu_items

  Parameters:  
- catalog_path (str) – (optional, never None) 
- operator (Literal['ADD', 'SWAP']) – 

Operator, The operator the asset menu will use (optional)

  
- `ADD` Add Node – Add a node to the active tree.. 
- `SWAP` Swap Node – Replace the selected nodes with the specified type..       template_modifier_asset_menu_items(*, catalog_path='', skip_essentials=False) 

template_modifier_asset_menu_items

  Parameters:  
- catalog_path (str) – (optional, never None) 
- skip_essentials (bool) – (optional)       template_node_operator_asset_menu_items(*, catalog_path='') 

template_node_operator_asset_menu_items

  Parameters: 

catalog_path (str) – (optional, never None)

      template_node_operator_asset_root_items() 

template_node_operator_asset_root_items

    template_texture_user() 

template_texture_user

    template_keymap_item_properties(item) 

template_keymap_item_properties

  Parameters: 

item ([`KeyMapItem`](bpy.types.KeyMapItem.html#bpy.types.KeyMapItem) | None) – (never None)

      template_component_menu(data, property, *, name='') 

Item. Display expanded property in a popup menu

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property 
- property (str) – Identifier of property in data (never None) 
- name (str) – (optional, never None)       template_colorspace_settings(data, property) 

Item. A widget to control input color space settings.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_colormanaged_view_settings(data, property) 

Item. A widget to control color managed view settings.

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_node_socket(*, color=(0.0, 0.0, 0.0, 1.0)) 

Node Socket Icon

  Parameters: 

color (Sequence[float]) – Color, (array of 4 items, in [0, 1], optional)

      template_cache_file(data, property) 

Item(s). User interface for selecting cache files and their source paths

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_cache_file_velocity(data, property) 

Show cache files velocity properties

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_cache_file_time_settings(data, property) 

Show cache files time settings

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_cache_file_layers(data, property) 

Show cache files override layers properties

  Parameters:  
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_recent_files(*, rows=6) 

Show list of recently saved .blend files

  Parameters: 

rows (int) – Maximum number of items to show (in [1, inf], optional)

  Returns: 

Number of items drawn (in [0, inf])

  Return type: 

int

      template_file_select_path(params) 

Item. A text button to set the active file browser path.

  Parameters: 

params ([`FileSelectParams`](bpy.types.FileSelectParams.html#bpy.types.FileSelectParams) | None) – File browser parameters whose path is edited

      template_event_from_keymap_item(item, *, text='', text_ctxt='', translate=True) 

Display keymap item as icons/text

  Parameters:  
- item ([`KeyMapItem`](bpy.types.KeyMapItem.html#bpy.types.KeyMapItem) | None) – Item, (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional)       template_light_linking_collection(context_layout, data, property) 

Visualization of a content of a light linking collection

  Parameters:  
- context_layout (`UILayout` | None) – Layout to set active list element as context properties (never None) 
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None)       template_bone_collection_tree() 

Show bone collections tree

    template_grease_pencil_layer_tree() 

View of the active Grease Pencil layer tree

    template_node_tree_interface(interface) 

Show a node tree interface

  Parameters: 

interface ([`NodeTreeInterface`](bpy.types.NodeTreeInterface.html#bpy.types.NodeTreeInterface) | None) – Node Tree Interface, Interface of a node tree to display (never None)

      template_node_inputs(node) 

Show a node settings and input socket values

  Parameters: 

node ([`Node`](bpy.types.Node.html#bpy.types.Node) | None) – Node, Display inputs of this node (never None)

      template_asset_shelf_popover(asset_shelf, *, name='', icon='NONE', icon_value=0) 

Create a button to open an asset shelf in a popover

  Parameters:  
- asset_shelf (str) – Identifier of the asset shelf to display (`bl_idname`) (never None) 
- name (str) – Optional name to indicate the active asset (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- icon_value (int) – Icon Value, Override automatic icon of the item (in [0, inf], optional)       template_popup_confirm(operator, *, text='', text_ctxt='', translate=True, icon='NONE', cancel_text='', cancel_default=False) 

Add confirm & cancel buttons into a popup which will close the popup when pressed

  Parameters:  
- operator (str) – Identifier of the operator (never None) 
- text (str) – Override automatic text of the item (optional) 
- text_ctxt (str) – Override automatic translation context of the given text (optional) 
- translate (bool) – Translate the given text, when UI translation is enabled (optional) 
- icon (Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]) – Icon, Override automatic icon of the item (optional) 
- cancel_text (str) – Optional text to use for the cancel, not shown when an empty string (optional, never None) 
- cancel_default (bool) – Cancel button by default (optional)   Returns: 

Operator properties to fill in

  Return type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties)

      template_shape_key_tree() 

Shape Key tree view

    classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
- id (str) – The RNA type identifier. 
- default ([`bpy.types.Struct`](bpy.types.Struct.html#bpy.types.Struct) | None) – The value to return when not found.   Returns: 

The RNA type or default when not found.

  Return type: 

[`bpy.types.Struct`](bpy.types.Struct.html#bpy.types.Struct)

      classmethod bl_rna_get_subclass_py(id, default=None, /)  Parameters:  
- id (str) – The RNA type identifier. 
- default (type | None) – The value to return when not found.   Returns: 

The class or default when not found.

  Return type: 

type

      introspect() 

Return a list of dictionaries containing a textual representation of the UI layout.

  Return type: 

list[dict[str, Any]]

      

## Inherited Properties

  
- [`bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data)       

## Inherited Functions

  
- [`bpy_struct.as_pointer`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer) 
- [`bpy_struct.driver_add`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add) 
- [`bpy_struct.driver_remove`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove) 
- [`bpy_struct.get`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.get) 
- [`bpy_struct.id_properties_clear`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear) 
- [`bpy_struct.id_properties_ensure`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure) 
- [`bpy_struct.id_properties_ui`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui) 
- [`bpy_struct.is_property_hidden`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden) 
- [`bpy_struct.is_property_overridable_library`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library) 
- [`bpy_struct.is_property_readonly`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly) 
- [`bpy_struct.is_property_set`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set) 
- [`bpy_struct.items`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.items)   
- [`bpy_struct.keyframe_delete`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete) 
- [`bpy_struct.keyframe_insert`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert) 
- [`bpy_struct.keys`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys) 
- [`bpy_struct.path_from_id`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id) 
- [`bpy_struct.path_from_module`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module) 
- [`bpy_struct.path_resolve`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve) 
- [`bpy_struct.pop`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop) 
- [`bpy_struct.property_overridable_library_set`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set) 
- [`bpy_struct.property_unset`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset) 
- [`bpy_struct.rna_ancestors`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors) 
- [`bpy_struct.type_recast`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast) 
- [`bpy_struct.values`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.values)     

## References

  
- [`AssetShelf.draw_context_menu`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.draw_context_menu) 
- [`Header.layout`](bpy.types.Header.html#bpy.types.Header.layout) 
- [`Menu.layout`](bpy.types.Menu.html#bpy.types.Menu.layout) 
- [`Node.draw_buttons`](bpy.types.Node.html#bpy.types.Node.draw_buttons) 
- [`Node.draw_buttons_ext`](bpy.types.Node.html#bpy.types.Node.draw_buttons_ext) 
- [`NodeInternal.draw_buttons`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons) 
- [`NodeInternal.draw_buttons_ext`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons_ext) 
- [`NodeSocket.draw`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.draw) 
- [`NodeSocketStandard.draw`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.draw) 
- [`NodeTreeInterfaceSocket.draw`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.draw) 
- [`NodeTreeInterfaceSocketBool.draw`](bpy.types.NodeTreeInterfaceSocketBool.html#bpy.types.NodeTreeInterfaceSocketBool.draw) 
- [`NodeTreeInterfaceSocketBundle.draw`](bpy.types.NodeTreeInterfaceSocketBundle.html#bpy.types.NodeTreeInterfaceSocketBundle.draw) 
- [`NodeTreeInterfaceSocketClosure.draw`](bpy.types.NodeTreeInterfaceSocketClosure.html#bpy.types.NodeTreeInterfaceSocketClosure.draw) 
- [`NodeTreeInterfaceSocketCollection.draw`](bpy.types.NodeTreeInterfaceSocketCollection.html#bpy.types.NodeTreeInterfaceSocketCollection.draw) 
- [`NodeTreeInterfaceSocketColor.draw`](bpy.types.NodeTreeInterfaceSocketColor.html#bpy.types.NodeTreeInterfaceSocketColor.draw) 
- [`NodeTreeInterfaceSocketFloat.draw`](bpy.types.NodeTreeInterfaceSocketFloat.html#bpy.types.NodeTreeInterfaceSocketFloat.draw) 
- [`NodeTreeInterfaceSocketFloatAngle.draw`](bpy.types.NodeTreeInterfaceSocketFloatAngle.html#bpy.types.NodeTreeInterfaceSocketFloatAngle.draw) 
- [`NodeTreeInterfaceSocketFloatColorTemperature.draw`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.html#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.draw) 
- [`NodeTreeInterfaceSocketFloatDistance.draw`](bpy.types.NodeTreeInterfaceSocketFloatDistance.html#bpy.types.NodeTreeInterfaceSocketFloatDistance.draw) 
- [`NodeTreeInterfaceSocketFloatFactor.draw`](bpy.types.NodeTreeInterfaceSocketFloatFactor.html#bpy.types.NodeTreeInterfaceSocketFloatFactor.draw) 
- [`NodeTreeInterfaceSocketFloatFrequency.draw`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.html#bpy.types.NodeTreeInterfaceSocketFloatFrequency.draw) 
- [`NodeTreeInterfaceSocketFloatMass.draw`](bpy.types.NodeTreeInterfaceSocketFloatMass.html#bpy.types.NodeTreeInterfaceSocketFloatMass.draw) 
- [`NodeTreeInterfaceSocketFloatPercentage.draw`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.html#bpy.types.NodeTreeInterfaceSocketFloatPercentage.draw) 
- [`NodeTreeInterfaceSocketFloatPixel.draw`](bpy.types.NodeTreeInterfaceSocketFloatPixel.html#bpy.types.NodeTreeInterfaceSocketFloatPixel.draw) 
- [`NodeTreeInterfaceSocketFloatTime.draw`](bpy.types.NodeTreeInterfaceSocketFloatTime.html#bpy.types.NodeTreeInterfaceSocketFloatTime.draw) 
- [`NodeTreeInterfaceSocketFloatTimeAbsolute.draw`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.html#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.draw) 
- [`NodeTreeInterfaceSocketFloatUnsigned.draw`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.html#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.draw) 
- [`NodeTreeInterfaceSocketFloatWavelength.draw`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.html#bpy.types.NodeTreeInterfaceSocketFloatWavelength.draw) 
- [`NodeTreeInterfaceSocketGeometry.draw`](bpy.types.NodeTreeInterfaceSocketGeometry.html#bpy.types.NodeTreeInterfaceSocketGeometry.draw) 
- [`NodeTreeInterfaceSocketImage.draw`](bpy.types.NodeTreeInterfaceSocketImage.html#bpy.types.NodeTreeInterfaceSocketImage.draw) 
- [`NodeTreeInterfaceSocketInt.draw`](bpy.types.NodeTreeInterfaceSocketInt.html#bpy.types.NodeTreeInterfaceSocketInt.draw) 
- [`NodeTreeInterfaceSocketIntFactor.draw`](bpy.types.NodeTreeInterfaceSocketIntFactor.html#bpy.types.NodeTreeInterfaceSocketIntFactor.draw) 
- [`NodeTreeInterfaceSocketIntPercentage.draw`](bpy.types.NodeTreeInterfaceSocketIntPercentage.html#bpy.types.NodeTreeInterfaceSocketIntPercentage.draw) 
- [`NodeTreeInterfaceSocketIntPixel.draw`](bpy.types.NodeTreeInterfaceSocketIntPixel.html#bpy.types.NodeTreeInterfaceSocketIntPixel.draw) 
- [`NodeTreeInterfaceSocketIntUnsigned.draw`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.html#bpy.types.NodeTreeInterfaceSocketIntUnsigned.draw) 
- [`NodeTreeInterfaceSocketIntVector2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVector2D.html#bpy.types.NodeTreeInterfaceSocketIntVector2D.draw) 
- [`NodeTreeInterfaceSocketIntVector3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVector3D.html#bpy.types.NodeTreeInterfaceSocketIntVector3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorFactor2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorFactor3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPercentage2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPercentage3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPixel2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorPixel3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.draw) 
- [`NodeTreeInterfaceSocketIntVectorUnsigned2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.draw) 
- [`NodeTreeInterfaceSocketIntVectorUnsigned3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.draw) 
- [`NodeTreeInterfaceSocketMaterial.draw`](bpy.types.NodeTreeInterfaceSocketMaterial.html#bpy.types.NodeTreeInterfaceSocketMaterial.draw) 
- [`NodeTreeInterfaceSocketMatrix.draw`](bpy.types.NodeTreeInterfaceSocketMatrix.html#bpy.types.NodeTreeInterfaceSocketMatrix.draw) 
- [`NodeTreeInterfaceSocketMenu.draw`](bpy.types.NodeTreeInterfaceSocketMenu.html#bpy.types.NodeTreeInterfaceSocketMenu.draw) 
- [`NodeTreeInterfaceSocketObject.draw`](bpy.types.NodeTreeInterfaceSocketObject.html#bpy.types.NodeTreeInterfaceSocketObject.draw) 
- [`NodeTreeInterfaceSocketRotation.draw`](bpy.types.NodeTreeInterfaceSocketRotation.html#bpy.types.NodeTreeInterfaceSocketRotation.draw) 
- [`NodeTreeInterfaceSocketShader.draw`](bpy.types.NodeTreeInterfaceSocketShader.html#bpy.types.NodeTreeInterfaceSocketShader.draw) 
- [`NodeTreeInterfaceSocketString.draw`](bpy.types.NodeTreeInterfaceSocketString.html#bpy.types.NodeTreeInterfaceSocketString.draw)   
- [`NodeTreeInterfaceSocketStringFilePath.draw`](bpy.types.NodeTreeInterfaceSocketStringFilePath.html#bpy.types.NodeTreeInterfaceSocketStringFilePath.draw) 
- [`NodeTreeInterfaceSocketTexture.draw`](bpy.types.NodeTreeInterfaceSocketTexture.html#bpy.types.NodeTreeInterfaceSocketTexture.draw) 
- [`NodeTreeInterfaceSocketVector.draw`](bpy.types.NodeTreeInterfaceSocketVector.html#bpy.types.NodeTreeInterfaceSocketVector.draw) 
- [`NodeTreeInterfaceSocketVector2D.draw`](bpy.types.NodeTreeInterfaceSocketVector2D.html#bpy.types.NodeTreeInterfaceSocketVector2D.draw) 
- [`NodeTreeInterfaceSocketVector4D.draw`](bpy.types.NodeTreeInterfaceSocketVector4D.html#bpy.types.NodeTreeInterfaceSocketVector4D.draw) 
- [`NodeTreeInterfaceSocketVectorAcceleration.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.draw) 
- [`NodeTreeInterfaceSocketVectorAcceleration2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.draw) 
- [`NodeTreeInterfaceSocketVectorAcceleration4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.draw) 
- [`NodeTreeInterfaceSocketVectorDirection.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection.html#bpy.types.NodeTreeInterfaceSocketVectorDirection.draw) 
- [`NodeTreeInterfaceSocketVectorDirection2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.draw) 
- [`NodeTreeInterfaceSocketVectorDirection4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.draw) 
- [`NodeTreeInterfaceSocketVectorEuler.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler.html#bpy.types.NodeTreeInterfaceSocketVectorEuler.draw) 
- [`NodeTreeInterfaceSocketVectorEuler2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.draw) 
- [`NodeTreeInterfaceSocketVectorEuler4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.draw) 
- [`NodeTreeInterfaceSocketVectorFactor.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor.html#bpy.types.NodeTreeInterfaceSocketVectorFactor.draw) 
- [`NodeTreeInterfaceSocketVectorFactor2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.draw) 
- [`NodeTreeInterfaceSocketVectorFactor4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.draw) 
- [`NodeTreeInterfaceSocketVectorPercentage.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage.draw) 
- [`NodeTreeInterfaceSocketVectorPercentage2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.draw) 
- [`NodeTreeInterfaceSocketVectorPercentage4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.draw) 
- [`NodeTreeInterfaceSocketVectorPixel.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel.html#bpy.types.NodeTreeInterfaceSocketVectorPixel.draw) 
- [`NodeTreeInterfaceSocketVectorPixel2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.draw) 
- [`NodeTreeInterfaceSocketVectorPixel4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.draw) 
- [`NodeTreeInterfaceSocketVectorTranslation.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation.draw) 
- [`NodeTreeInterfaceSocketVectorTranslation2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.draw) 
- [`NodeTreeInterfaceSocketVectorTranslation4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.draw) 
- [`NodeTreeInterfaceSocketVectorVelocity.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity.draw) 
- [`NodeTreeInterfaceSocketVectorVelocity2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.draw) 
- [`NodeTreeInterfaceSocketVectorVelocity4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.draw) 
- [`NodeTreeInterfaceSocketVectorXYZ.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ.draw) 
- [`NodeTreeInterfaceSocketVectorXYZ2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.draw) 
- [`NodeTreeInterfaceSocketVectorXYZ4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.draw) 
- [`Operator.layout`](bpy.types.Operator.html#bpy.types.Operator.layout) 
- [`Panel.layout`](bpy.types.Panel.html#bpy.types.Panel.layout) 
- `UILayout.box` 
- `UILayout.column` 
- `UILayout.column_flow` 
- `UILayout.grid_flow` 
- `UILayout.menu_pie` 
- `UILayout.panel` 
- `UILayout.panel` 
- `UILayout.panel_prop` 
- `UILayout.panel_prop` 
- `UILayout.row` 
- `UILayout.split` 
- `UILayout.template_light_linking_collection` 
- [`UIList.draw_filter`](bpy.types.UIList.html#bpy.types.UIList.draw_filter) 
- [`UIList.draw_item`](bpy.types.UIList.html#bpy.types.UIList.draw_item) 
- [`UIPieMenu.layout`](bpy.types.UIPieMenu.html#bpy.types.UIPieMenu.layout) 
- [`UIPopover.layout`](bpy.types.UIPopover.html#bpy.types.UIPopover.layout) 
- [`UIPopupMenu.layout`](bpy.types.UIPopupMenu.html#bpy.types.UIPopupMenu.layout)
