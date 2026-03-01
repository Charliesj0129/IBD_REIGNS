#!/usr/bin/env python3
import os

# Base directory for SVGs
OUT_DIR = "assets/characters"

# Base style for all SVGs: viewBox 0 0 100 100, single color currentColor
SVG_TEMPLATE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="currentColor">{path}</svg>\n'

# Abstract geometric paths for silhouettes
# They should just be a combination of <path>, <circle>, etc.
ASSETS = {
    # Default: basic person
    "default.svg": '<path d="M50 20 A15 15 0 1 0 50 50 A15 15 0 1 0 50 20 M25 90 C25 60 75 60 75 90 Z"/>',
    
    # Doctor: Person with stethoscope
    "doctor.svg": '<path d="M50 15 A12 12 0 1 0 50 39 A12 12 0 1 0 50 15 M25 90 C25 60 75 60 75 90 Z"/>'
                  '<path d="M35 55 Q50 80 65 55" fill="none" stroke="currentColor" stroke-width="3"/>'
                  '<circle cx="65" cy="55" r="4"/>',
                  
    # Nurse: Person with nurse cap
    "nurse.svg": '<path d="M50 22 A12 12 0 1 0 50 46 A12 12 0 1 0 50 22 M35 22 L65 22 L60 10 L40 10 Z M30 90 C30 65 70 65 70 90 Z"/>'
                 '<path d="M47 13 L53 13 M50 10 L50 16" stroke="var(--color-bg)" stroke-width="2"/>',
                 
    # Boss/Manager: Person with sharp shoulders/tie
    "boss.svg": '<path d="M50 18 A13 13 0 1 0 50 44 A13 13 0 1 0 50 18 M20 90 L35 55 L65 55 L80 90 Z"/>'
                '<path d="M50 55 L45 70 L50 85 L55 70 Z" fill="var(--color-bg)"/>',
                
    # Colleague/Coworker: Glasses and casual
    "colleague.svg": '<path d="M50 20 A14 14 0 1 0 50 48 A14 14 0 1 0 50 20 M25 90 C25 65 75 65 75 90 Z"/>'
                     '<rect x="36" y="28" width="12" height="6" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
                     '<rect x="52" y="28" width="12" height="6" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
                     '<line x1="48" y1="31" x2="52" y2="31" stroke="currentColor" stroke-width="2"/>',

    # Family: Softer, larger or double silhouette for warmth
    "family.svg": '<path d="M40 25 A12 12 0 1 0 40 49 A12 12 0 1 0 40 25 M15 90 C15 65 65 65 65 90 Z"/>'
                  '<path d="M70 35 A9 9 0 1 0 70 53 A9 9 0 1 0 70 35 M50 90 C55 70 85 70 90 90 Z"/>',

    # Friend: Casul, hoodie or beanie (abstract)
    "friend.svg": '<path d="M50 18 A14 14 0 1 0 50 46 A14 14 0 1 0 50 18 M20 90 C20 75 40 55 50 55 C60 55 80 75 80 90 Z"/>'
                  '<path d="M40 18 Q50 5 60 18 L50 22 Z" fill="currentColor"/>',

    # System / Concept (complication, flare, event): Abstract warning/medical cross/eye
    "system.svg": '<path d="M50 10 L90 80 L10 80 Z" fill="none" stroke="currentColor" stroke-width="8"/>'
                  '<circle cx="50" cy="45" r="5"/><rect x="47" y="55" width="6" height="15" rx="3"/>',

    # Inner Voice: Abstract brain/cloud or thought bubble
    "inner_voice.svg": '<path d="M50 80 Q20 80 20 60 Q20 40 40 40 Q40 20 60 20 Q80 20 80 40 Q90 50 80 65 Q90 80 50 80 Z" fill="none" stroke="currentColor" stroke-width="6"/>'
                       '<circle cx="35" cy="55" r="4"/> <circle cx="50" cy="45" r="3"/> <circle cx="65" cy="48" r="4"/>',
                       
    # Insurance/Money: Coin/Document
    "insurance.svg": '<path d="M30 15 L70 15 L70 85 L30 85 Z" fill="none" stroke="currentColor" stroke-width="6"/>'
                     '<line x1="40" y1="30" x2="60" y2="30" stroke="currentColor" stroke-width="4"/>'
                     '<line x1="40" y1="45" x2="60" y2="45" stroke="currentColor" stroke-width="4"/>'
                     '<circle cx="50" cy="65" r="8"/>',
                     
    # Treatment / Pill / Biologic: Drop/Pill/Needle
    "treatment.svg": '<path d="M50 20 L65 50 A15 15 0 0 1 35 50 Z" />'
                     '<rect x="40" y="60" width="20" height="8" rx="4"/>'
                     '<rect x="40" y="75" width="20" height="8" rx="4"/>'
}

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    for filename, path_data in ASSETS.items():
        out_path = os.path.join(OUT_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(SVG_TEMPLATE.format(path=path_data))
        print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
