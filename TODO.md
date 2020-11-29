# To do

## Add support for SLA attributes

### Layer

- [ ] `groupClips` **undocumented**

### Page

- [ ] `LEFT` For multipage spreads, which page in the spread is the left most  **(no examples of non 0 value)**

### Page objects

- [ ] `path` for non-rect object
- [ ] `copath` for non-rect object

#### Symbol

- [ ] `pattern` Pattern name to use *(str)*

#### Text

- [ ] `PLTSHOW` (optional) Set to 1 if the path of a Text on a path should be shown
- [ ] `BASEOF` (optional) Offset for the text from its path for text on a path **(not the same as character style BASEO)**
- [ ] `FLOP` **undocumented**
- [ ] `textPathType` **undocumented**
- [ ] `textPathFlipped` **undocumented**

#### Image

- [ ] `IRENDER` (optional) Rendering Intent for Images. 0 = Perceptual; 1 = Relative Colorimetric; 2 = Saturation; 3 = Absolute Colorimetric
- [ ] `EPROF` (optional) Embedded ICC-Profile for images *(str, name of the profile)*
- [ ] `Pagenumber` **undocumented**
- [ ] `COMPRESSIONMETHOD` **undocumented**

#### Polygon, Polyline

- [ ] `fillRule` **undocumented**

#### Polyline

- [ ] `NUMDASH` Number of entries in DASH *(int)*
- [ ] `DASHOFF` (optional) Offset for the first dash *(float)*
- [ ] `DASHS` List of dash values, see the PostScript manual for details *(list of floats separated by spaces)*
- [ ] `TransValue` (optional) Transparency value for fill 
- [ ] `TransValueS` (optional) Transparency value for stroke
- [ ] `TEXTFLOWMODE` **undocumented**

### Styles

#### Paragraph style

- [ ] `DROP` Has drop cap *(bool 0 or 1)*
- [ ] `DROPLIN` Number of lines for a drop cap *(int)*
- [ ] `OpticalMargins` Whether to use optical margins 
- [ ] `BCOLOR` **undocumented**
- [ ] `BSHADE` **undocumented**
- [ ] `BSHADE` **undocumented**
- [ ] `DIRECTION` **undocumented**
- [ ] `ParagraphEffectOffset` **undocumented**

That should be implemented :

- [ ] `LINESP`

##### Common with character style

- [x] `TXTSHX` Text shadow offset horizontally
- [x] `TXTSHY` Text shadow offset vertically
- [x] `TXTOUT` Outline width
- [x] `TXTULP` Underline offset
- [x] `TXTULW` Underline width
- [x] `TXTSTP` Strikethrough offset
- [x] `TXTSTW` Strikethrough width

#### Character style

- [ ] `SCOLOR` Stroke color *(foreground str)*
- [ ] `SSHADE` Stroke shade *(foreground opacity 100)*
- [ ] `BGCOLOR` **undocumented**
- [ ] `BGSHADE` **undocumented**
- [ ] `HyphenWordMin` **undocumented**

##### Without GUI elements to modify them

- [ ] `BASEO ` Offset from baseline *(dim, pica, 0 ?)*
- [x] `TXTSHX` Text shadow offset horizontally
- [x] `TXTSHY` Text shadow offset vertically
- [x] `TXTOUT` Outline width
- [x] `TXTULP` Underline offset
- [x] `TXTULW` Underline width
- [x] `TXTSTP` Strikethrough offset
- [x] `TXTSTW` Strikethrough width

<!-- vim:set spl=en: -->
