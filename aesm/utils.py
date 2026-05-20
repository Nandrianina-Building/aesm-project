import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime

from django.core.files import File
from django.core.files.base import ContentFile

W, H = A4  # 595 x 842 pts

# ═══════════════════════════════════════════════════════
# CHARTE GRAPHIQUE CENTRALISÉE (Modifiable à volonté)
# ═══════════════════════════════════════════════════════
# Couleurs (r, g, b en 0..1) - Thème Document Administratif Sobre
C_PRIMARY       = (0.05, 0.05, 0.05)  # Presque noir (En-tête, titres principaux, pied de page)
C_SECONDARY     = (0.25, 0.25, 0.25)  # Gris foncé (Titres de sections)
C_TEXT          = (0.15, 0.15, 0.15)  # Noir doux pour le texte principal
C_MUTED         = (0.45, 0.45, 0.45)  # Gris moyen pour les labels
C_WHITE         = (1.00, 1.00, 1.00)  # Blanc
C_BG_LIGHT      = (0.97, 0.97, 0.97)  # Gris très clair pour les fonds de blocs
C_BORDER        = (0.85, 0.85, 0.85)  # Gris clair pour les bordures

# Statut - Couleurs du badge de validation
C_STATUS_BG     = (0.95, 0.95, 0.95)  # Fond du badge
C_STATUS_BORDER = (0.75, 0.75, 0.75)  # Bordure du badge
C_STATUS_TEXT   = (0.10, 0.10, 0.10)  # Texte du badge

# Polices standards
F_REGULAR = "Helvetica"
F_BOLD    = "Helvetica-Bold"


# ═══════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return File(buf, name='qr.png')


def _rect(p, x, y, w, h, fill=None, stroke=None, radius=0, lw=0.5):
    p.saveState()
    if fill:
        p.setFillColorRGB(*fill)
    if stroke:
        p.setStrokeColorRGB(*stroke)
        p.setLineWidth(lw)
    if radius:
        p.roundRect(x, y, w, h, radius,
                    fill=1 if fill else 0,
                    stroke=1 if stroke else 0)
    else:
        p.rect(x, y, w, h,
               fill=1 if fill else 0,
               stroke=1 if stroke else 0)
    p.restoreState()


def _row(p, label, value, x, y, col_gap=160):
    """Dessine un couple label / valeur aligné."""
    p.saveState()
    p.setFont(F_REGULAR, 9)
    p.setFillColorRGB(*C_MUTED)
    p.drawString(x, y, label)
    p.setFont(F_BOLD, 10)
    p.setFillColorRGB(*C_TEXT)
    p.drawString(x + col_gap, y, str(value) if value else "—")
    p.restoreState()


# ═══════════════════════════════════════════════════════
# GÉNÉRATION DU LOGICIEL PDF
# ═══════════════════════════════════════════════════════
def generate_pdf(transaction_id, qr_code, etudiant, paiement=None):
    buf  = BytesIO()
    p    = canvas.Canvas(buf, pagesize=A4)
    p.setTitle(f"Quitus AESM – {transaction_id}")

    now      = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    annee    = now.strftime("%Y")

    margin = 40   # Marges latérales de sécurité
    inner  = W - margin * 2

    # ── SECTION 1 — EN-TÊTE ADMINISTRATIF ──
    hdr_bottom = H - 130
    hdr_h      = 130

    _rect(p, 0, hdr_bottom, W, hdr_h, fill=C_PRIMARY)

    # Sigle Principal
    p.saveState()
    p.setFont(F_BOLD, 34)
    p.setFillColorRGB(*C_WHITE)
    p.drawString(margin, H - 55, "AESM")
    p.setFont(F_REGULAR, 9)
    p.setFillColorRGB(*C_BORDER)
    p.drawString(margin, H - 72, "Association des Étudiants en Sociologie de Madagascar")
    p.restoreState()

    # Titre Centré Officiel
    p.saveState()
    p.setFillColorRGB(*C_WHITE)
    p.setFont(F_BOLD, 16)
    p.drawCentredString(W / 2, H - 98, "QUITUS D'ADHÉSION")
    p.setFont(F_REGULAR, 10)
    p.setFillColorRGB(*C_BORDER)
    p.drawCentredString(W / 2, H - 116, f"Année académique {annee}")
    p.restoreState()

    # ── SECTION 2 — BANDEAU D'AVERTISSEMENT ──
    band_y = hdr_bottom - 26
    _rect(p, margin, band_y, inner, 22, fill=C_BG_LIGHT, stroke=C_BORDER, radius=4)

    p.saveState()
    p.setFont(F_BOLD, 8)
    p.setFillColorRGB(*C_PRIMARY)
    txt = "DOCUMENT OFFICIEL — À CONSERVER PRÉCIEUSEMENT"
    p.drawCentredString(W / 2, band_y + 7, txt)
    p.restoreState()

    # ── SECTION 3 — INFORMATIONS DU MEMBRE ──
    sec3_top = band_y - 18

    p.saveState()
    p.setFont(F_BOLD, 10)
    p.setFillColorRGB(*C_SECONDARY)
    p.drawString(margin, sec3_top, "INFORMATIONS DU MEMBRE")
    p.setStrokeColorRGB(*C_SECONDARY)
    p.setLineWidth(1.5)
    p.line(margin, sec3_top - 4, margin + 160, sec3_top - 4)
    p.restoreState()

    card3_h  = 130
    card3_y  = sec3_top - card3_h - 14
    _rect(p, margin, card3_y, inner, card3_h, fill=C_WHITE, stroke=C_BORDER, radius=6)

    row_x  = margin + 14
    row_y0 = card3_y + card3_h - 24
    gap    = 22

    _row(p, "Numéro de matricule :", etudiant.matricule,        row_x, row_y0)
    _row(p, "Nom :",                 etudiant.user.last_name,   row_x, row_y0 - gap)
    _row(p, "Prénom :",              etudiant.user.first_name,  row_x, row_y0 - gap * 2)
    _row(p, "Adresse électronique :", etudiant.user.email,       row_x, row_y0 - gap * 3)
    _row(p, "Statut de l'adhérent :", "Membre Actif",           row_x, row_y0 - gap * 4)

    # ── SECTION 4 — DÉTAILS DU RÈGLEMENT ──
    sec4_top = card3_y - 22

    p.saveState()
    p.setFont(F_BOLD, 10)
    p.setFillColorRGB(*C_SECONDARY)
    p.drawString(margin, sec4_top, "DÉTAILS DE LA TRANSACTION")
    p.setStrokeColorRGB(*C_SECONDARY)
    p.setLineWidth(1.5)
    p.line(margin, sec4_top - 4, margin + 175, sec4_top - 4)
    p.restoreState()

    card4_h = 110
    card4_y = sec4_top - card4_h - 14
    _rect(p, margin, card4_y, inner, card4_h, fill=C_BG_LIGHT, stroke=C_BORDER, radius=6)

    row4_x  = margin + 14
    row4_y0 = card4_y + card4_h - 24

    montant = f"{paiement.montant} Ar" if paiement else "2 000 Ar"
    statut  = paiement.statut          if paiement else "Validé"

    _row(p, "Référence de transaction :", str(transaction_id), row4_x, row4_y0)
    _row(p, "Montant de la cotisation :", montant,              row4_x, row4_y0 - gap)
    _row(p, "Date effective du paiement :", date_str,           row4_x, row4_y0 - gap * 2)

    # Aligné sur l'architecture globale
    p.saveState()
    p.setFont(F_REGULAR, 9)
    p.setFillColorRGB(*C_MUTED)
    p.drawString(row4_x, row4_y0 - gap * 3, "Statut du règlement :")
    
    bx = row4_x + 160
    by = row4_y0 - gap * 3 - 3
    _rect(p, bx, by, 70, 16, fill=C_STATUS_BG, stroke=C_STATUS_BORDER, radius=4)
    p.setFont(F_BOLD, 9)
    p.setFillColorRGB(*C_STATUS_TEXT)
    p.drawString(bx + 8, by + 4, str(statut).upper())
    p.restoreState()

    # ── SECTION 5 — ENCADRÉ DE CERTIFICATION ──
    cert_y = card4_y - 24
    _rect(p, margin, cert_y - 44, inner, 56, fill=C_WHITE, stroke=C_BORDER, radius=6)

    p.saveState()
    p.setFont(F_REGULAR, 9)
    p.setFillColorRGB(*C_TEXT)
    lines = [
        f"Le présent quitus certifie que le titulaire est officiellement enregistré en tant que membre de l'AESM",
        f"pour l'année académique {annee}. Il lui confère le plein accès aux services et activités de l'association.",
        "Ce document administratif est généré automatiquement par le système de gestion.",
    ]
    for i, line in enumerate(lines):
        p.drawCentredString(W / 2, cert_y - 10 - i * 14, line)
    p.restoreState()

    # ── SECTION 6 — SÉCURITÉ & ANALYSE QR ──
    qr_sec_y = cert_y - 44 - 20

    # Ligne de démarcation
    p.saveState()
    p.setStrokeColorRGB(*C_BORDER)
    p.setLineWidth(0.8)
    p.setDash([4, 4])
    p.line(margin, qr_sec_y, W - margin, qr_sec_y)
    p.restoreState()

    p.saveState()
    p.setFont(F_BOLD, 9)
    p.setFillColorRGB(*C_SECONDARY)
    p.drawCentredString(W / 2, qr_sec_y - 18, "CONTRÔLE ET VÉRIFICATION D'AUTHENTICITÉ")
    p.restoreState()

    qr_size = 110
    qr_x    = (W - qr_size) / 2
    qr_y    = qr_sec_y - 18 - qr_size - 12

    # Cadre de protection du QR code
    _rect(p, qr_x - 10, qr_y - 10, qr_size + 20, qr_size + 20, fill=C_WHITE, stroke=C_BORDER, radius=4)

    # Affichage du flux image
    qr_code.seek(0)
    img_reader = ImageReader(BytesIO(qr_code.read()))
    p.drawImage(img_reader, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True)

    p.saveState()
    p.setFont(F_REGULAR, 8)
    p.setFillColorRGB(*C_MUTED)
    p.drawCentredString(W / 2, qr_y - 16, "Veuillez numériser ce code afin de vérifier la validité des informations.")
    p.setFont(F_BOLD, 8)
    p.setFillColorRGB(*C_PRIMARY)
    p.drawCentredString(W / 2, qr_y - 28, f"Identifiant unique : {transaction_id}")
    p.restoreState()

    # ── SECTION 7 — MENTIONS LÉGALES ET PIED DE PAGE ──
    _rect(p, 0, 0, W, 52, fill=C_PRIMARY)

    p.saveState()
    p.setFont(F_BOLD, 9)
    p.setFillColorRGB(*C_WHITE)
    p.drawCentredString(W / 2, 36, "AESM — Association des Étudiants en Sociologie de Madagascar")
    p.setFont(F_REGULAR, 8)
    p.setFillColorRGB(*C_BORDER)
    p.drawCentredString(W / 2, 22, f"Émis automatiquement le {date_str} • Document officiel infalsifiable")
    p.drawCentredString(W / 2, 10, "Université d'Antananarivo • Département de Sociologie")
    p.restoreState()

    # Finalisation du document
    p.showPage()
    p.save()

    return ContentFile(
        buf.getvalue(),
        name=f'quitus_{transaction_id}.pdf'
    )
