# To do

## Add support for SLA attributes

### Layer

- [ ] `groupClips` **<undocumented>**

### Page

- [ ] `LEFT` For multipage spreads, which page in the spread is the left most  **(no examples of non 0 value)**

### Page objects

- [ ] `path` for non-rect object
- [ ] `copath` for non-rect object

#### Symbol

- [ ] `pattern` Pattern name to use *(str)*

#### Text

- [ ] `FLOP` **<undocumented>**
- [ ] `textPathType` **<undocumented>**
- [ ] `textPathFlipped` **<undocumented>**
- [ ] `PLTSHOW` (optional) Set to 1 if the path of a Text on a path should be shown
- [ ] `BASEOF` (optional) Offset for the text from its path for text on a path **(not the same as character style BASEO)**

#### Image

- [ ] `Pagenumber` **<undocumented>**
- [ ] `IRENDER` (optional) Rendering Intent for Images. 0 = Perceptual; 1 = Relative Colorimetric; 2 = Saturation; 3 = Absolute Colorimetric

#### Polygon, Polyline

- [ ] `fillRule` **<undocumented>**

#### Polyline

- [ ] `NUMDASH` Number of entries in DASH *(int)*
- [ ] `DASHOFF` (optional) Offset for the first dash *(float)*
- [ ] `DASHS` List of dash values, see the PostScript manual for details *(list of floats separated by spaces)*
- [ ] `TEXTFLOWMODE` **<undocumented>**
- [ ] `TransValue` (optional) Transparency value for fill 
- [ ] `TransValueS` (optional) Transparency value for stroke

### Styles

#### Paragraph style

- [ ] `DROP` Has drop cap *(bool 0 or 1)*
- [ ] `DROPLIN` Number of lines for a drop cap *(int)*
- [ ] `ParagraphEffectOffset` **<undocumented>**

#### Character style

- [ ] `SCOLOR` Stroke color *(foreground str)*
- [ ] `SSHADE` Stroke shade *(foreground opacity 100)*

##### Without GUI elements to modify them

- [ ] `BASEO ` Offset from baseline *(dim, pica, 0 ?)*
- [ ] `TXTSHX` Text shadow offset horizontally
- [ ] `TXTSHY` Text shadow offset vertically
- [ ] `TXTOUT` Outline width
- [ ] `TXTULP` Underline offset
- [ ] `TXTULW` Underline width
- [ ] `TXTSTP` Strikethrough offset
- [ ] `TXTSTW` Strikethrough width

<!-- vim:set spl=en: -->
