"""Industrial photonics product catalog — laser and terahertz systems."""

PHOTONICS_CATALOG = [
    # =========================================================================
    # LASER TECHNOLOGY
    # =========================================================================
    # --- Single Frequency Lasers ---
    {
        "id": "cobolt-04-01",
        "name": "Cobolt 04-01 Series",
        "category": "Single Frequency CW DPSS Lasers",
        "type": "laser",
        "wavelengths": [457, 473, 491, 514, 532, 561, 594, 660, 1064],
        "power_range_mw": [25, 450],
        "noise_rms_percent": 0.3,
        "linewidth": "Ultra-narrow (SLM)",
        "named_models": [
            "Cobolt Twist (457 nm)", "Cobolt Blues (473 nm)", "Cobolt Calypso (491 nm)",
            "Cobolt Fandango (514 nm)", "Cobolt Samba (532 nm)", "Cobolt Jive (561 nm)",
            "Cobolt Mambo (594 nm)", "Cobolt Flamenco (660 nm)", "Cobolt Rumba (1064 nm)",
        ],
        "applications": [
            "Fluorescence Microscopy", "Raman Spectroscopy", "Holography",
            "Interferometry", "Flow Cytometry",
        ],
        "key_features": [
            "Single longitudinal mode (SLM)", "HTCure hermetically sealed",
            "Long coherence length", "Ultra-robust package",
        ],
        "keywords": ["dpss", "cw", "continuous wave", "single frequency", "cobolt"],
    },
    {
        "id": "cobolt-05-01",
        "name": "Cobolt 05-01 Series",
        "category": "High-Power Single Frequency CW DPSS Lasers",
        "type": "laser",
        "wavelengths": [320, 349, 355, 457, 473, 491, 515, 532, 561, 640, 660, 1064],
        "power_range_mw": [20, 3000],
        "noise_rms_percent": 0.1,
        "linewidth": "< 1 MHz",
        "beam_quality_m2": 1.1,
        "named_models": [
            "Cobolt Kizomba (349 nm)", "Cobolt Zydeco (355 nm)",
            "Cobolt Samba (532 nm, up to 1.5 W)", "Cobolt Jive (561 nm, up to 1 W)",
            "Cobolt Bolero (640 nm)", "Cobolt Rumba (1064 nm, up to 3 W)",
        ],
        "applications": [
            "Raman Spectroscopy", "Interferometry", "Holography",
            "Super-Resolution Microscopy", "Optical Tweezers", "Flow Cytometry",
            "DNA Sequencing", "Fluorescence Microscopy",
        ],
        "key_features": [
            "Up to 3 W output power", "Spectral purity > 60 dB",
            "Perfect TEM00 beam", "HTCure sealed design", "UV to NIR coverage",
        ],
        "keywords": ["dpss", "high power", "single frequency", "cw", "uv", "cobolt"],
    },
    # --- Diode Lasers ---
    {
        "id": "cobolt-06-01",
        "name": "Cobolt 06-01 Series",
        "category": "Modulated CW Diode Lasers",
        "type": "laser",
        "wavelengths": [
            375, 395, 405, 415, 425, 445, 457, 473, 488, 505, 515, 520,
            532, 553, 561, 633, 638, 647, 660, 685, 690, 705, 730, 760,
            785, 808, 830, 940, 975,
        ],
        "power_range_mw": [25, 400],
        "noise_rms_percent": 0.2,
        "modulation_mhz": 150,
        "rise_time_ns": 300,
        "applications": [
            "Confocal Microscopy", "Flow Cytometry", "DNA Sequencing",
            "Spinning Disc Microscopy", "TIRF Microscopy", "Optogenetics",
        ],
        "key_features": [
            "25+ wavelengths available", "Digital modulation DC to 150 MHz",
            "True OFF capability", "Plug-and-play with USB/RS-232",
            "Integrated clean-up filters",
        ],
        "keywords": ["diode", "modulated", "fast switching", "mld", "dpl", "06-01", "multi-color"],
    },
    # --- Narrow Linewidth Lasers ---
    {
        "id": "cobolt-08-01",
        "name": "Cobolt 08-01 Series",
        "category": "Narrow Linewidth CW Lasers",
        "type": "laser",
        "wavelengths": [405, 457, 473, 488, 515, 532, 561, 633, 660, 785, 1064],
        "power_range_mw": [40, 500],
        "noise_rms_percent": 0.1,
        "linewidth": "< 100 kHz",
        "spectral_purity_db": 70,
        "named_models": [
            "Cobolt Disco (785 nm, < 100 kHz)", "08-DPL (488/532 nm, > 80 dB purity)",
            "08-NLD (633 nm, integrated isolator)",
        ],
        "applications": [
            "Raman Spectroscopy", "Interferometry", "Metrology",
            "Semiconductor Inspection",
        ],
        "key_features": [
            "Linewidth < 100 kHz", "Spectral purity > 70 dB",
            "No ASE background", "Integrated isolator (NLD models)",
            "Immune to optical feedback",
        ],
        "keywords": ["narrow linewidth", "08-dpl", "08-nld", "disco", "raman", "high purity"],
    },
    # --- Nanosecond / Pulsed Lasers ---
    {
        "id": "cobolt-tor",
        "name": "Cobolt Tor Series",
        "category": "Q-Switched Nanosecond Pulsed Lasers",
        "type": "laser",
        "wavelengths": [355, 532, 1064],
        "power_range_mw": [100, 1000],
        "pulse_energy_uj": [50, 500],
        "pulse_length_ns": [1, 5],
        "repetition_rate_khz": 7,
        "applications": [
            "Photoacoustic Microscopy", "Marking", "LIDAR",
            "LIBS (Laser-Induced Breakdown Spectroscopy)",
        ],
        "key_features": [
            "Passively Q-switched", "1-5 ns pulse length",
            "Up to 500 uJ/pulse", "Compact ring-cavity design",
            "Low jitter, high stability",
        ],
        "keywords": ["pulsed", "nanosecond", "q-switched", "ns", "lidar", "libs", "marking"],
    },
    # --- Tunable Lasers ---
    {
        "id": "c-wave",
        "name": "C-WAVE Series",
        "category": "Widely Tunable CW OPO Lasers",
        "type": "laser",
        "wavelengths_range": [450, 3400],
        "tunable": True,
        "linewidth": "< 1 MHz (< 500 kHz GTR)",
        "power_range_mw": [80, 4000],
        "noise_rms_percent": 1.0,
        "variants": [
            "C-WAVE VIS LP/HP (450-650 nm + 900-1300 nm)",
            "C-WAVE IR LP/HP (infrared)",
            "C-WAVE NIR (near-infrared, 780 nm pump)",
            "C-WAVE GTR (500-750 nm + 1000-3400 nm, simultaneous outputs)",
            "C-WAVE BTS (700-1000 nm, up to 4 W, Ti:Sapphire pump)",
        ],
        "applications": [
            "Quantum Optics", "Atomic Physics", "Spectroscopy",
            "Nanophotonics", "Holography", "Interferometry", "Metrology",
        ],
        "key_features": [
            "450 nm to 3.4 um continuous tuning", "Mode-hop-free operation",
            "Narrow linewidth < 1 MHz", "Multiple pump laser options",
            "AbsoluteLambda wavelength stabilization",
        ],
        "keywords": ["tunable", "opo", "quantum", "atom", "c-wave"],
    },
    {
        "id": "cobolt-qu-t",
        "name": "Cobolt Qu-T Series",
        "category": "Tunable & Lockable CW Lasers",
        "type": "laser",
        "wavelengths_range": [530, 850],
        "tunable": True,
        "power_range_mw": [100, 500],
        "applications": [
            "Quantum Optics", "Atomic Physics", "Spectroscopy",
        ],
        "key_features": [
            "Tunable AND lockable", "530-850 nm range",
            "Perfect TEM00 beam", "Mode-hop-free tuning",
        ],
        "keywords": ["tunable", "lockable", "quantum", "atom trapping", "qu-t"],
    },
    {
        "id": "cobolt-odin",
        "name": "Cobolt Odin Series",
        "category": "Mid-IR Tunable Pulsed Lasers",
        "type": "laser",
        "wavelengths_range": [3000, 4600],
        "tunable": True,
        "power_range_mw": [1, 80],
        "repetition_rate_khz": 7,
        "applications": [
            "Gas Analysis", "Mid-IR Spectroscopy", "Environmental Monitoring",
        ],
        "key_features": [
            "3-4.6 um mid-infrared", "Wavelength-selectable",
            "Compact design", "High repetition rate",
        ],
        "keywords": ["mid-ir", "infrared", "gas analysis", "odin"],
    },
    # --- Laser Combiners ---
    {
        "id": "c-flex",
        "name": "C-FLEX Laser Combiner",
        "category": "Multi-Wavelength Laser Combiners",
        "type": "laser",
        "wavelengths": "Custom (up to 8 lines from 375-1064 nm)",
        "platforms": ["C4 (up to 4 lasers)", "C6 (up to 6 lasers)", "C8 (up to 8 lasers)"],
        "power_range_mw": [25, 1000],
        "applications": [
            "Confocal Microscopy", "Super-Resolution Imaging",
            "Flow Cytometry", "Optogenetics",
        ],
        "key_features": [
            "Up to 8 laser lines combined", "Single collinear output",
            "Mix diode + DPSS technology", "32 wavelengths available",
            "Fully customizable",
        ],
        "keywords": ["combiner", "multi-line", "multi-color", "c-flex", "multiline"],
    },
    # --- Femtosecond Lasers ---
    {
        "id": "valo",
        "name": "VALO Femtosecond Series",
        "category": "Ultrafast Fiber Lasers",
        "type": "laser",
        "wavelengths_range": [1000, 1100],
        "power_range_mw": [500, 3000],
        "pulse_duration_fs": 40,
        "peak_power_mw": 2000000,
        "applications": [
            "Multiphoton Microscopy", "Nonlinear Imaging",
            "Two-Photon Excitation", "SHG Imaging",
        ],
        "key_features": [
            "< 40 fs pulse duration", "Peak power > 2 MW",
            "Turn-key operation", "Compact fiber laser design",
        ],
        "keywords": ["femtosecond", "ultrafast", "fs", "multiphoton", "two-photon", "valo"],
    },
    # --- Fiber Lasers / Amplifiers ---
    {
        "id": "ampheia",
        "name": "Ampheia Fiber Laser Systems",
        "category": "High-Power CW Fiber Amplifiers",
        "type": "laser",
        "wavelengths": [488, 515, 532, 976, 1015, 1030, 1064],
        "power_range_mw": [5000, 50000],
        "noise_rms_percent": 0.05,
        "linewidth": "< 100 kHz",
        "applications": [
            "Quantum Optics", "Atomic Physics", "Atom Cooling & Trapping",
            "Laser Doppler Velocimetry", "Holography", "Metrology",
            "Semiconductor Inspection",
        ],
        "key_features": [
            "Up to 50 W output power", "Ultra-low RIN",
            "Single-frequency single-mode", "Integrated seed laser",
            "Outstanding pointing stability",
        ],
        "keywords": ["fiber", "amplifier", "high power", "ampheia", "watt"],
    },
    # =========================================================================
    # TERAHERTZ TECHNOLOGY
    # =========================================================================
    {
        "id": "t-spectralyzer",
        "name": "T-SPECTRALYZER",
        "category": "THz Time-Domain Spectrometers",
        "type": "terahertz",
        "frequency_range_thz": [0.1, 4.0],
        "dynamic_range_db": 70,
        "spectral_resolution_ghz": 5,
        "measurement_time_s": [2, 8],
        "geometries": ["Transmission (T)", "Reflection (R)", "Fiber-coupled (F)"],
        "applications": [
            "THz Spectroscopy", "Non-Destructive Testing",
            "Chemical Identification", "Material Characterization",
            "Quality Control", "Layer Thickness Measurement",
        ],
        "key_features": [
            "0.1-4 THz range", "Dynamic range > 70 dB",
            "Plug & play fiber-based", "T/R/F measurement geometries",
            "Fully automated", "Contact-free, non-destructive",
        ],
        "keywords": ["terahertz", "thz", "spectrometer", "spectroscopy", "ndt"],
    },
    {
        "id": "t-spectralyzer-f",
        "name": "T-SPECTRALYZER F",
        "category": "Compact Fiber-Based THz Spectrometers",
        "type": "terahertz",
        "frequency_range_thz": [0.1, 2.5],
        "dynamic_range_db": 54,
        "spectral_resolution_ghz": 10,
        "form_factor": "19-inch rack module",
        "applications": [
            "THz Spectroscopy", "Non-Destructive Testing",
            "In-Line Process Monitoring", "Quality Control",
        ],
        "key_features": [
            "Compact 19-inch rack format", "0.1-2.5 THz range",
            "Fast scan (0.05-5 s)", "Fiber-coupled modules",
            "Industrial integration ready",
        ],
        "keywords": ["terahertz", "thz", "compact", "inline", "process monitoring", "rack"],
    },
    {
        "id": "t-cognition",
        "name": "T-COGNITION",
        "category": "Security THz Spectrometers",
        "type": "terahertz",
        "frequency_range_thz": [0.1, 4.0],
        "applications": [
            "Security Screening", "Drug Detection", "Explosives Detection",
            "Mail & Package Inspection", "Customs Inspection",
        ],
        "key_features": [
            "Spectroscopic fingerprint identification", "Internal substance database",
            "Non-invasive (no opening required)", "Instant identification",
            "DIN C4 envelope capacity",
        ],
        "keywords": ["security", "screening", "detection"],
    },
    {
        "id": "t-sense",
        "name": "T-SENSE",
        "category": "THz Mail & Package Imagers",
        "type": "terahertz",
        "throughput": "Up to 3,000 envelopes/hour",
        "applications": [
            "Mail Screening", "Security Scanning", "Package Inspection",
        ],
        "key_features": [
            "Radiation-free (no X-rays)", "Up to 3,000 envelopes/hour",
            "Dual-filter display", "Mobile and flexible",
            "Scalable from office to postal center",
        ],
        "keywords": ["security", "mail", "screening", "xray-free"],
    },
    {
        "id": "t-sense-fmi",
        "name": "T-SENSE FMI",
        "category": "THz Industrial Imaging Systems",
        "type": "terahertz",
        "applications": [
            "Industrial Quality Control", "Foreign Body Detection",
            "Flaw & Defect Detection", "Zero-Defect Production",
            "Non-Destructive Testing",
        ],
        "key_features": [
            "Non-destructive imaging", "Amplitude AND phase analysis",
            "No ionizing radiation", "Touchscreen control",
            "Adaptable for zero-defect production",
        ],
        "keywords": ["quality control", "ndt", "imaging", "defect", "production"],
    },
]


def get_all_products():
    """Return all products in the catalog."""
    return PHOTONICS_CATALOG


def get_product_by_id(product_id):
    """Return a single product by its ID."""
    for product in PHOTONICS_CATALOG:
        if product["id"] == product_id:
            return product
    return None


def get_products_by_type(product_type):
    """Return products filtered by type ('laser' or 'terahertz')."""
    return [p for p in PHOTONICS_CATALOG if p.get("type") == product_type]


def search_products(spec_text):
    """Search products by matching keywords from spec against catalog fields.

    Returns list of dicts with 'product' and 'score' keys, sorted by score desc.
    """
    import re

    spec_lower = spec_text.lower()
    results = []

    for product in PHOTONICS_CATALOG:
        score = 0

        # --- Application matching (high value) ---
        for app in product.get("applications", []):
            if app.lower() in spec_lower:
                score += 20
            else:
                app_words = [w for w in app.lower().split() if len(w) > 3]
                matching_words = sum(1 for w in app_words if w in spec_lower)
                if matching_words >= 2:
                    score += 12
                elif matching_words == 1 and len(app_words) <= 2:
                    score += 6

        # --- Feature keyword matching ---
        for feature in product.get("key_features", []):
            for word in feature.lower().split():
                if len(word) > 3 and word in spec_lower:
                    score += 4

        # --- Category matching ---
        if product["category"].lower() in spec_lower:
            score += 15
        else:
            cat_words = [w for w in product["category"].lower().split() if len(w) > 3]
            if sum(1 for w in cat_words if w in spec_lower) >= 2:
                score += 8

        # --- Product-specific keyword matching ---
        for kw in product.get("keywords", []):
            if kw.lower() in spec_lower:
                score += 10

        # --- Named model matching ---
        for model_name in product.get("named_models", []):
            name_part = model_name.split("(")[0].strip().lower()
            if name_part in spec_lower:
                score += 30

        # --- Wavelength matching (numeric, nm) ---
        wavelengths = product.get("wavelengths", [])
        if isinstance(wavelengths, list):
            for wl in wavelengths:
                if str(wl) in spec_lower:
                    score += 25

        # --- Wavelength range matching ---
        wl_range = product.get("wavelengths_range", [])
        if wl_range:
            numbers = re.findall(r"\d+", spec_lower)
            for num_str in numbers:
                num = int(num_str)
                if wl_range[0] <= num <= wl_range[1]:
                    score += 20

        # --- THz frequency matching ---
        freq_range = product.get("frequency_range_thz", [])
        if freq_range:
            thz_keywords = ["terahertz", "thz"]
            if any(kw in spec_lower for kw in thz_keywords):
                score += 30

        # --- Power matching (mW and W) ---
        power_range = product.get("power_range_mw", [])
        if power_range:
            power_matches = re.findall(r"(\d+)\s*(?:mw|milliwatt)", spec_lower)
            for pm in power_matches:
                power_val = int(pm)
                if power_range[0] <= power_val <= power_range[1]:
                    score += 20
                elif power_val < power_range[0] * 2:
                    score += 5

            watt_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:w|watt)\b", spec_lower)
            for wm in watt_matches:
                power_mw = float(wm) * 1000
                if power_range[0] <= power_mw <= power_range[1]:
                    score += 20

        # --- Tunable keyword matching ---
        if product.get("tunable") and any(
            kw in spec_lower for kw in ["tunable", "tuning"]
        ):
            score += 25

        # --- Pulsed / femtosecond matching ---
        if product.get("pulse_length_ns") or product.get("pulse_duration_fs"):
            pulsed_kw = ["pulsed", "nanosecond", "ns-", "q-switch"]
            if any(kw in spec_lower for kw in pulsed_kw):
                score += 20

        if product.get("pulse_duration_fs"):
            fs_kw = ["femtosecond", "ultrafast", "multiphoton"]
            if any(kw in spec_lower for kw in fs_kw):
                score += 25

        # --- Modulation matching ---
        if product.get("modulation_mhz"):
            mod_kw = ["modulation", "modulated", "fast switching"]
            if any(kw in spec_lower for kw in mod_kw):
                score += 20

        # --- Security / screening matching ---
        security_kw = ["security", "screening", "mail"]
        if any(kw in spec_lower for kw in security_kw):
            if product.get("type") == "terahertz":
                score += 15

        # --- Product name direct matching ---
        product_name_lower = product["name"].lower()
        if product_name_lower in spec_lower:
            score += 35

        if score > 0:
            max_possible = 120
            normalized_score = min(round((score / max_possible) * 100), 99)
            results.append({"product": product, "score": normalized_score})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
