import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime

from django.core.files import File
from django.core.files.base import ContentFile


W, H = A4  # 595 x 842 pts

# ── Couleurs (r, g, b en 0..1) ──
C_BLUE_DARK  = (0.10, 0.12, 0.66)
C_BLUE_MID   = (0.18, 0.21, 0.79)
C_BLUE_LIGHT = (0.55, 0.60, 1.00)
C_WHITE      = (1.00, 1.00, 1.00)
C_BG         = (0.95, 0.96, 0.99)
C_BORDER     = (0.85, 0.87, 0.94)
C_TEXT       = (0.15, 0.15, 0.20)
C_MUTED      = (0.45, 0.47, 0.55)
C_GREEN      = (0.09, 0.60, 0.30)


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


def _fill(p, color):
    p.setFillColorRGB(*color)

def _stroke(p, color):
    p.setStrokeColorRGB(*color)

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
    """Dessine label + valeur sur une même ligne."""
    p.saveState()
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(*C_MUTED)
    p.drawString(x, y, label)
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(*C_TEXT)
    p.drawString(x + col_gap, y, str(value) if value else "—")
    p.restoreState()


def generate_pdf(transaction_id, qr_code, etudiant, paiement=None):
    buf  = BytesIO()
    p    = canvas.Canvas(buf, pagesize=A4)
    p.setTitle(f"Quitus AESM – {transaction_id}")

    now      = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    annee    = now.strftime("%Y")

    margin = 40   # marge gauche/droite
    inner  = W - margin * 2  # largeur utile

    # ═══════════════════════════════════════════════════════
    # SECTION 1 — EN-TÊTE  (y de 842 à 700)
    # ═══════════════════════════════════════════════════════
    hdr_top    = H          # 842
    hdr_bottom = H - 130    # 712
    hdr_h      = 130

    _rect(p, 0, hdr_bottom, W, hdr_h, fill=C_BLUE_DARK)

    # Cercles décoratifs
    p.saveState()
    p.setFillColorRGB(*C_BLUE_MID)
    p.circle(W - 50, H - 30, 80, fill=1, stroke=0)
    p.circle(W - 10, H - 105, 45, fill=1, stroke=0)
    p.restoreState()

    # Sigle
    p.saveState()
    p.setFont("Helvetica-Bold", 34)
    p.setFillColorRGB(*C_WHITE)
    p.drawString(margin, H - 55, "AESM")
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(*C_BLUE_LIGHT)
    p.drawString(margin, H - 70, "Association des Étudiants en Sociologie de Madagascar")
    p.restoreState()

    # Titre centré
    p.saveState()
    p.setFillColorRGB(*C_WHITE)
    p.setFont("Helvetica-Bold", 16)
    titre = "QUITUS D'ADHÉSION"
    p.drawCentredString(W / 2, H - 100, titre)
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(*C_BLUE_LIGHT)
    p.drawCentredString(W / 2, H - 116, f"Année académique {annee}")
    p.restoreState()

    # ═══════════════════════════════════════════════════════
    # SECTION 2 — BANDEAU OFFICIEL  (y: 700 → 680)
    # ═══════════════════════════════════════════════════════
    band_y = hdr_bottom - 26   # 686
    _rect(p, margin, band_y, inner, 22, fill=C_BG, stroke=C_BORDER, radius=4)

    p.saveState()
    p.setFont("Helvetica-BoldOblique", 8)
    p.setFillColorRGB(*C_BLUE_DARK)
    txt = "★  DOCUMENT OFFICIEL — VEUILLEZ CONSERVER CE DOCUMENT  ★"
    p.drawCentredString(W / 2, band_y + 7, txt)
    p.restoreState()

    # ═══════════════════════════════════════════════════════
    # SECTION 3 — INFORMATIONS MEMBRE  (y: 670 → 530)
    # ═══════════════════════════════════════════════════════
    sec3_top = band_y - 18    # 668

    # Titre section
    p.saveState()
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(*C_BLUE_DARK)
    p.drawString(margin, sec3_top, "INFORMATIONS DU MEMBRE")
    p.setStrokeColorRGB(*C_BLUE_DARK)
    p.setLineWidth(2)
    p.line(margin, sec3_top - 4, margin + 190, sec3_top - 4)
    p.setStrokeColorRGB(*C_BLUE_LIGHT)
    p.setLineWidth(1)
    p.line(margin + 190, sec3_top - 4, margin + 230, sec3_top - 4)
    p.restoreState()

    # Carte membre
    card3_h  = 130
    card3_y  = sec3_top - card3_h - 14    # 524
    _rect(p, margin, card3_y, inner, card3_h, fill=C_WHITE, stroke=C_BORDER, radius=6)

    # Lignes de données — espacées de 22pts
    row_x  = margin + 14
    row_y0 = card3_y + card3_h - 24   # première ligne
    gap    = 22

    _row(p, "Matricule :",  etudiant.matricule,            row_x, row_y0)
    _row(p, "Nom :",        etudiant.user.last_name,       row_x, row_y0 - gap)
    _row(p, "Prénom :",     etudiant.user.first_name,      row_x, row_y0 - gap * 2)
    _row(p, "Email :",      etudiant.user.email,            row_x, row_y0 - gap * 3)
    _row(p, "Statut :",     "Membre Actif ✓",              row_x, row_y0 - gap * 4)

    # ═══════════════════════════════════════════════════════
    # SECTION 4 — TRANSACTION  (y: 510 → 400)
    # ═══════════════════════════════════════════════════════
    sec4_top = card3_y - 22    # 502

    p.saveState()
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(*C_BLUE_DARK)
    p.drawString(margin, sec4_top, "DÉTAILS DE LA TRANSACTION")
    p.setStrokeColorRGB(*C_BLUE_DARK)
    p.setLineWidth(2)
    p.line(margin, sec4_top - 4, margin + 215, sec4_top - 4)
    p.setStrokeColorRGB(*C_BLUE_LIGHT)
    p.setLineWidth(1)
    p.line(margin + 215, sec4_top - 4, margin + 255, sec4_top - 4)
    p.restoreState()

    card4_h = 110
    card4_y = sec4_top - card4_h - 14    # 378
    _rect(p, margin, card4_y, inner, card4_h, fill=C_BG, stroke=C_BORDER, radius=6)

    row4_x  = margin + 14
    row4_y0 = card4_y + card4_h - 24

    montant = f"{paiement.montant} Ar" if paiement else "2 000 Ar"
    statut  = paiement.statut          if paiement else "Validé"

    _row(p, "N° Transaction :", str(transaction_id), row4_x, row4_y0)
    _row(p, "Montant :",        montant,              row4_x, row4_y0 - gap)
    _row(p, "Date de paiement :", date_str,           row4_x, row4_y0 - gap * 2)

    # Statut avec badge vert
    p.saveState()
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(*C_MUTED)
    p.drawString(row4_x, row4_y0 - gap * 3, "Statut :")
    # Badge vert
    bx = row4_x + 160
    by = row4_y0 - gap * 3 - 3
    _rect(p, bx, by, 70, 16, fill=(0.88, 1.00, 0.92), stroke=(0.65, 0.90, 0.70), radius=4)
    p.setFont("Helvetica-Bold", 9)
    p.setFillColorRGB(*C_GREEN)
    p.drawString(bx + 8, by + 4, f"✓  {statut}")
    p.restoreState()

    # ═══════════════════════════════════════════════════════
    # SECTION 5 — TEXTE DE CERTIFICATION  (y: 365 → 310)
    # ═══════════════════════════════════════════════════════
    cert_y = card4_y - 24    # 354

    _rect(p, margin, cert_y - 44, inner, 56, fill=(0.97, 0.97, 1.00), stroke=C_BORDER, radius=6)

    p.saveState()
    p.setFont("Helvetica-BoldOblique", 9)
    p.setFillColorRGB(*C_TEXT)
    lines = [
        f"Ce document certifie que le titulaire est officiellement membre de l'AESM",
        f"pour l'année académique {annee}. Il lui confère l'accès à l'ensemble des",
        "services et activités de l'association. Document généré automatiquement.",
    ]
    for i, line in enumerate(lines):
        p.drawCentredString(W / 2, cert_y - 8 - i * 14, line)
    p.restoreState()

    # ═══════════════════════════════════════════════════════
    # SECTION 6 — QR CODE  (y: 290 → 90)
    # ═══════════════════════════════════════════════════════
    qr_sec_y = cert_y - 44 - 20    # 290

    # Séparateur pointillé
    p.saveState()
    p.setStrokeColorRGB(*C_BORDER)
    p.setLineWidth(0.8)
    p.setDash([5, 4])
    p.line(margin, qr_sec_y, W - margin, qr_sec_y)
    p.restoreState()

    # Titre QR
    p.saveState()
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(*C_BLUE_DARK)
    p.drawCentredString(W / 2, qr_sec_y - 18, "VÉRIFICATION D'AUTHENTICITÉ")
    p.restoreState()

    # QR code centré
    qr_size = 120
    qr_x    = (W - qr_size) / 2
    qr_y    = qr_sec_y - 18 - qr_size - 16   # en dessous du titre

    # Cadre blanc
    _rect(p, qr_x - 10, qr_y - 10, qr_size + 20, qr_size + 20,
          fill=C_WHITE, stroke=C_BORDER, radius=8)

    # Image QR
    qr_code.seek(0)
    img_reader = ImageReader(BytesIO(qr_code.read()))
    p.drawImage(img_reader, qr_x, qr_y, width=qr_size, height=qr_size,
                preserveAspectRatio=True)

    # Texte sous QR
    p.saveState()
    p.setFont("Helvetica", 8)
    p.setFillColorRGB(*C_MUTED)
    p.drawCentredString(W / 2, qr_y - 18, "Scannez ce QR code pour vérifier l'authenticité du document")
    p.setFont("Helvetica-Bold", 8)
    p.setFillColorRGB(*C_BLUE_DARK)
    p.drawCentredString(W / 2, qr_y - 30, f"Réf. : {transaction_id}")
    p.restoreState()

    # ═══════════════════════════════════════════════════════
    # SECTION 7 — PIED DE PAGE  (y: 0 → 52)
    # ═══════════════════════════════════════════════════════
    _rect(p, 0, 0, W, 52, fill=C_BLUE_DARK)

    p.saveState()
    p.setFont("Helvetica-Bold", 9)
    p.setFillColorRGB(*C_WHITE)
    p.drawCentredString(W / 2, 36, "AESM — Association des Étudiants en Sociologie de Madagascar")
    p.setFont("Helvetica", 8)
    p.setFillColorRGB(*C_BLUE_LIGHT)
    p.drawCentredString(W / 2, 22, f"Document généré le {date_str}  •  Ce document est officiel et infalsifiable")
    p.drawCentredString(W / 2, 10, "Université d'Antananarivo  •  Département de Sociologie")
    p.restoreState()

    # ═══════════════════════════════════════════════════════
    p.showPage()
    p.save()

    return ContentFile(
        buf.getvalue(),
        name=f'quitus_{transaction_id}.pdf'
    )