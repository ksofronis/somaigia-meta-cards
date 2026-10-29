"""Shoe taxonomy for Meta product sets: season / category / gender / segment from feed title, product_type, custom_label_0, brand.
Written to the labels supplementary feed as custom_label_1..4 (empty in the client feed)."""
import re
CAT = [  # (category, regex on title), first match wins; title beats product_type (653 items sit under bare ΑΝΑΤΟΜΙΚΑ)
    ('Σαμπό', r'σαμπ[οό]|τσ[οό]καρ'),
    ('Ειδικά υποδήματα', r'διαβητικ|μετεγχειρ|ορθοπεδικ|αποφ[οό]ρτισ|θεραπευτικ'),
    ('Μπότες - Μποτάκια', r'μπ[οό]τ(α|ες|ακι)'),
    ('Παντόφλες', r'παντ[οό]φλ'),
    ('Πέδιλα', r'π[εέ]διλ'),
    ('Σανδάλια', r'σανδ[αά]λ|σαγιον[αά]ρ'),
    ('Πλατφόρμες', r'πλατφ[οό]ρμ|flatform|εσπαντρ[ιί]γ'),
    ('Γόβες', r'γ[οό]β[αε]'),
    ('Μοκασίνια - Loafers', r'μοκασ[ιί]ν|loafer'),
    ('Μπαλαρίνες', r'μπαλαρ[ιί]ν|μπαρ[εέ]τα'),
    ('Sneakers', r'sneaker|αθλητικ|walk it'),
    ('Casual', r'casual|slip-on'),
]
PT = [('Σαμπό', r'ΣΑΜΠΟ'), ('Ειδικά υποδήματα', r'ΕΙΔΙΚΑ ΥΠΟΔΗΜΑΤΑ|Διαβητικά'), ('Μπότες - Μποτάκια', r'Μπότες'), ('Παντόφλες', r'Παντόφλες'),
      ('Πέδιλα', r'Πέδιλα'), ('Σανδάλια', r'Σανδάλια|Σαγιονάρες'), ('Πλατφόρμες', r'Πλατφόρμες|Flatforms|Εσπαντρίγιες'), ('Γόβες', r'Γόβες'),
      ('Μοκασίνια - Loafers', r'Μοκασίνια'), ('Μπαλαρίνες', r'Μπαλαρίνες'), ('Sneakers', r'Sneakers'), ('Casual', r'Casual|Slip-On|ΑΝΑΤΟΜΙΚΑ|Προσφορές')]
NOT_SHOE = r'ΕΥΕΞΙΑ|ΠΕΡΙΠΟΙΗΣΗ'
SUMMER_CATS = {'Πέδιλα', 'Σανδάλια', 'Πλατφόρμες'}

def classify(title, ptype, season0, brand):
    """-> dict(season, category, gender, segment) or None for non-shoe items."""
    if re.search(NOT_SHOE, ptype) or re.search(r'κ[αά]λτσ|καλσ[οό]ν|γ[αά]ντι|κουβ[εέ]ρτ', title, re.I): return None
    cat = next((c for c, rx in CAT if re.search(rx, title, re.I)), None) or next((c for c, rx in PT if re.search(rx, ptype)), None)
    if not cat: return None
    s = {'Ανοιξη-Καλοκαίρι': 'Καλοκαιρινά', 'Φθινόπωρο-Χειμώνας': 'Χειμερινά', 'Όλο το χρόνο': 'Όλο το χρόνο'}.get(season0.strip())
    if cat in SUMMER_CATS or 'Καλοκαιρινές' in ptype: s = 'Καλοκαιρινά'  # open shoes never count as in-season in winter, whatever the label says
    elif 'Χειμερινές' in ptype or (not s and cat == 'Μπότες - Μποτάκια'): s = 'Χειμερινά'
    s = s or 'Όλο το χρόνο'
    gender = 'Παιδικά' if re.search(r'ΠΑΙΔΙΚΑ', ptype) or re.search(r'walk it', title, re.I) else \
             'Γυναικεία' if re.search(r'ΓΥΝΑΙΚΕΙΑ|Γυναικεία', ptype) else 'Ανδρικά' if re.search(r'ΑΝΔΡΙΚΑ|Ανδρικά', ptype) else 'Unisex'
    segment = 'Celia Ruiz' if 'celia' in brand.lower() else 'Σαμπό' if cat == 'Σαμπό' else 'Ειδικά' if cat == 'Ειδικά υποδήματα' or 'ΕΙΔΙΚΑ' in ptype else 'Ανατομικά'
    return dict(season=s, category=cat, gender=gender, segment=segment)
