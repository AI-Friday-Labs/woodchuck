# openai/gpt-5.6-terra - medium

A woodchuck would chuck **about 700 lb of wood**—the traditional answer—**if** it could chuck wood as efficiently as it excavates a burrow.

That famous estimate comes from New York wildlife technician **Richard Thomas’s** 1988 calculation: a typical woodchuck burrow involves moving roughly **35 ft³** of material, weighing about **700 lb**. It is a charming extrapolation, not a measured wood-throwing experiment; real woodchucks (*Marmota monax*) dig soil and may move small sticks, but do not routinely fell, carry, or throw logs.

## Assumptions and estimate

| Assumption | Value / interpretation |
|---|---:|
| “Chuck” means | Move/displace material over a burrow-building season, not throw it a specified distance |
| Animal | An adult woodchuck / groundhog (*Marmota monax*) |
| Excavated volume | **35 ft³** ≈ **0.99 m³** |
| Traditional mass estimate | **700 lb** ≈ **318 kg** |
| Wood model | Same *volume* as a burrow, filled with seasoned mixed hardwood |
| Representative wood density | **35 lb/ft³** ≈ **560 kg/m³** |

### Results

1. **Traditional riddle answer:**  
   **700 lb**, or about **318 kg** of wood.

2. **Volume-equivalent physics estimate:**  
   If the woodchuck moved a burrow’s volume of actual wood—**35 ft³** or **0.99 m³**—and the wood averaged **35 lb/ft³**, it would be:

   \[
   35\ \text{ft}^3 \times 35\ \text{lb/ft}^3 = 1{,}225\ \text{lb}
   \]

   So: **about 1,225 lb**, or **556 kg**, of wood.

The difference matters: Thomas’s **700 lb** is based on the mass of excavated earth. A full **35 ft³** of ordinary hardwood usually weighs more than that.

## Uncertainty

This is uncertain by at least a factor of about two because burrow sizes, soil conditions, wood species, moisture, branch size, and the meaning of “chuck” all vary.

Using plausible ranges:

- Burrow-equivalent volume: **20–50 ft³** (**0.57–1.42 m³**)
- Wood density: **25–47 lb/ft³** (**400–753 kg/m³**)

Estimated wood moved:

- **500–2,350 lb**
- **227–1,066 kg**

A defensible concise answer is therefore:

> **About 700 lb (318 kg) by tradition; about 1,200 lb (560 kg) if “a burrow’s volume of average hardwood” is meant literally.**

## Sources

- Thomas, Richard. 1988 woodchuck-burrow extrapolation, commonly cited by the New York State Department of Environmental Conservation and popular accounts of the riddle; basis for the traditional **35 ft³ / 700 lb** result.  
- U.S. Department of Agriculture, Forest Products Laboratory, *Wood Handbook: Wood as an Engineering Material*, General Technical Report FPL-GTR-190, especially density tables for common woods. https://www.fpl.fs.usda.gov/documnts/fplgtr/fpl_gtr190.pdf  
- Encyclopaedia Britannica, “groundhog,” for the identification of the woodchuck as *Marmota monax*. https://www.britannica.com/animal/groundhog

## Haiku

Groundhog paws at logs  
Almost one cubic meter  
Winter keeps the rest  

## Pirate summary

Arrr! By the old burrow reckonin’, the furry digger’d chuck **700 pounds** o’ timber—about **318 kilograms**. But fill a whole burrow’s worth with proper hardwood, matey, and ye may be lookin’ at **1,225 pounds**, or **556 kilograms**!

```json
{
  "question": "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
  "short_answer": {
    "traditional_estimate": {
      "imperial": "700 lb",
      "SI": "318 kg",
      "basis": "Richard Thomas's 1988 extrapolation from approximately 35 ft³ of burrow excavation."
    },
    "volume_equivalent_wood_estimate": {
      "imperial": "1,225 lb of wood",
      "SI": "556 kg of wood",
      "volume": {
        "imperial": "35 ft³",
        "SI": "0.99 m³"
      },
      "basis": "35 ft³ multiplied by an assumed seasoned mixed-hardwood density of 35 lb/ft³."
    }
  },
  "assumptions": [
    {
      "name": "Meaning of chuck",
      "value": "To excavate, move, or displace material over a burrow-building season; not to throw wood a specified distance."
    },
    {
      "name": "Animal",
      "value": "Adult woodchuck/groundhog, Marmota monax."
    },
    {
      "name": "Burrow-equivalent volume",
      "imperial": "35 ft³",
      "SI": "0.99 m³"
    },
    {
      "name": "Representative wood density",
      "imperial": "35 lb/ft³",
      "SI": "560 kg/m³",
      "material": "Seasoned mixed hardwood"
    }
  ],
  "calculation": {
    "formula": "mass = volume × density",
    "imperial": "35 ft³ × 35 lb/ft³ = 1,225 lb",
    "SI": "0.99 m³ × 560 kg/m³ ≈ 556 kg"
  },
  "uncertainty": {
    "reason": "Burrow volume, wood species, moisture content, wood shape, and the definition of 'chuck' are variable.",
    "plausible_volume_range": {
      "imperial": "20–50 ft³",
      "SI": "0.57–1.42 m³"
    },
    "plausible_density_range": {
      "imperial": "25–47 lb/ft³",
      "SI": "400–753 kg/m³"
    },
    "resulting_mass_range": {
      "imperial": "500–2,350 lb",
      "SI": "227–1,066 kg"
    }
  },
  "haiku": [
    "Groundhog paws at logs",
    "Almost one cubic meter",
    "Winter keeps the rest"
  ],
  "pirate_summary": "Arrr! The old answer be 700 pounds, or 318 kilograms; a whole burrow's volume of hardwood could weigh nearer 1,225 pounds, or 556 kilograms.",
  "sources": [
    {
      "citation": "Thomas, Richard (1988), traditional 35 ft³ / 700 lb woodchuck-burrow extrapolation."
    },
    {
      "citation": "USDA Forest Products Laboratory, Wood Handbook: Wood as an Engineering Material, FPL-GTR-190.",
      "url": "https://www.fpl.fs.usda.gov/documnts/fplgtr/fpl_gtr190.pdf"
    },
    {
      "citation": "Encyclopaedia Britannica, Groundhog.",
      "url": "https://www.britannica.com/animal/groundhog"
    }
  ]
}
```
