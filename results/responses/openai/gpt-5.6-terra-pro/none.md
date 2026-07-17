# openai/gpt-5.6-terra-pro - none

A woodchuck (also called a groundhog, *Marmota monax*) does not normally “chuck” wood. It digs burrows, moving soil rather than logs. The famous estimate comes from New York State wildlife expert Richard Thomas, who reportedly calculated that a woodchuck excavating a typical burrow moves about **700 lb of earth**. If it could chuck wood at an equivalent rate, it would chuck roughly that mass of wood.

### Assumptions
1. “Chuck” means **move or excavate** material over the construction of one typical burrow.
2. A typical woodchuck burrow involves about **700 lb** of displaced material.
3. The hypothetical woodchuck can move wood with the same **mass-handling capacity** as soil.
4. “Wood” is treated as bulk material; actual volume depends strongly on species, moisture, and whether it is logs, chips, or split firewood.

### Estimate
- **Mass:** about **700 lb**
- **SI mass:** about **318 kg**

Using representative wood densities:

| Wood condition | Approximate density | Volume equivalent of 318 kg |
|---|---:|---:|
| Dry softwood | 400 kg/m³ | 0.80 m³ |
| Typical seasoned hardwood | 650 kg/m³ | 0.49 m³ |
| Green/dense hardwood | 900 kg/m³ | 0.35 m³ |

So the usual answer is:

> **A woodchuck would chuck about 700 pounds of wood, if a woodchuck could chuck wood.**

In volume, that is roughly:

- **0.35–0.80 m³ of wood**
- **12–28 ft³ of solid wood**
- About **0.1–0.25 cord**, depending on wood type and stacking convention.

### Uncertainty
This is necessarily speculative. A reasonable uncertainty range is at least **±50%**, because:
- burrow sizes vary greatly;
- soil mass estimates vary by depth and moisture;
- wood is mechanically harder to grasp, cut, and move than loose earth;
- “chuck” has no standardized scientific definition.

Thus a defensible estimate is:

- **350–1,050 lb**
- **160–480 kg**
- roughly **0.2–1.2 m³**, depending on wood density and handling assumptions.

### Haiku
Groundhog lifts bark—  
If paws could master timber,  
Seven hundred pounds.

### Pirate summary
Arrr, if the little landlubber could chuck timber like it digs its burrow, it’d chuck about **700 pounds o’ wood**—that be **318 kilograms**, give or take a fair bit o’ sawdust.

```json
{
  "question": "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
  "common_estimate": {
    "imperial_mass": {
      "value": 700,
      "unit": "lb"
    },
    "si_mass": {
      "value": 318,
      "unit": "kg"
    }
  },
  "assumptions": [
    "A woodchuck is a groundhog (Marmota monax).",
    "Chuck is interpreted as moving material during excavation.",
    "A typical burrow displaces approximately 700 lb of soil.",
    "The hypothetical animal can move wood at the same mass rate as soil."
  ],
  "wood_volume_equivalent": {
    "range_si": {
      "min": 0.35,
      "max": 0.8,
      "unit": "m^3"
    },
    "range_imperial": {
      "min": 12,
      "max": 28,
      "unit": "ft^3"
    },
    "depends_on": [
      "wood species",
      "moisture content",
      "whether wood is solid, split, or chipped"
    ]
  },
  "uncertainty": {
    "estimated_relative_uncertainty": "approximately +/- 50%",
    "mass_range_imperial": {
      "min": 350,
      "max": 1050,
      "unit": "lb"
    },
    "mass_range_si": {
      "min": 160,
      "max": 480,
      "unit": "kg"
    }
  },
  "source_note": "The 700 lb figure is commonly attributed to wildlife expert Richard Thomas, based on a woodchuck's typical burrow excavation.",
  "conclusion": "About 700 lb (318 kg) of wood, under the conventional burrow-excavation analogy."
}
```
