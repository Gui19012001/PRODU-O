# ============================================================
# NR-17 | ERGONOMIA POR VISÃO - MVP 04.1 TABLET / CLOUD
# Arquivo único: visão + RULA/REBA + evidências + PDF
# Câmera otimizada para tablet: traseira, 16:9 e IA em resolução reduzida
# ============================================================

from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, KeepTogether
)

NAVY = colors.HexColor('#0B1F33')
NAVY2 = colors.HexColor('#12314E')
CYAN = colors.HexColor('#18A7C9')
LIGHT = colors.HexColor('#EEF4F8')
MID = colors.HexColor('#667A8B')
GRID = colors.HexColor('#D7E1E8')
RED = colors.HexColor('#C83B3B')
ORANGE = colors.HexColor('#D97916')
GREEN = colors.HexColor('#238B57')


def _fmt_seconds(seconds):
    seconds = max(0, int(float(seconds or 0)))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f'{h:02d}:{m:02d}:{s:02d}' if h else f'{m:02d}:{s:02d}'


def _fmt_angle(value):
    if value is None or value == '':
        return '--'
    try:
        return f'{float(value):.1f} deg'
    except Exception:
        return str(value)


def _score_color(label):
    text = str(label or '').lower()
    if any(x in text for x in ['imediata', 'muito alto', 'critico', 'crítico']):
        return RED
    if any(x in text for x in ['alto', 'breve']):
        return ORANGE
    if any(x in text for x in ['medio', 'médio', 'investigar']):
        return colors.HexColor('#B18A00')
    return GREEN


def generate_nr17_pdf(pdf_path, metadata, snapshot, rula_result, reba_result, evidence, critical_pose=None):
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        'NRTitle', parent=styles['Title'], fontName='Helvetica-Bold',
        fontSize=20, leading=23, textColor=NAVY, alignment=TA_LEFT, spaceAfter=5,
    )
    subtitle = ParagraphStyle(
        'NRSub', parent=styles['Normal'], fontName='Helvetica',
        fontSize=9, leading=13, textColor=MID, spaceAfter=10,
    )
    h2 = ParagraphStyle(
        'NRH2', parent=styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=12, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=7,
    )
    body = ParagraphStyle(
        'NRBody', parent=styles['BodyText'], fontName='Helvetica',
        fontSize=8.7, leading=12, textColor=NAVY,
    )
    small = ParagraphStyle(
        'NRSmall', parent=body, fontSize=7.5, leading=10, textColor=MID,
    )
    center = ParagraphStyle(
        'NRCenter', parent=body, alignment=TA_CENTER,
    )

    assessment_id = str(metadata.get('avaliacao_id', ''))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(GRID)
        canvas.line(18*mm, 14*mm, A4[0]-18*mm, 14*mm)
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(MID)
        canvas.drawString(18*mm, 9*mm, f'Ergonomia por Visao - Avaliacao {assessment_id}')
        canvas.drawRightString(A4[0]-18*mm, 9*mm, f'Pagina {doc.page}')
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=17*mm, bottomMargin=18*mm,
        title=f'Relatorio de Ergonomia {assessment_id}',
        author=str(metadata.get('avaliador', '') or 'Sistema NR-17 - Visao'),
    )

    story = []
    story.append(Paragraph('RELATORIO DE ACOMPANHAMENTO ERGONOMICO', title))
    story.append(Paragraph(
        'Visao computacional + indicadores de exposicao + RULA/REBA assistidos. '
        'Documento de apoio tecnico: nao substitui AEP, AET ou avaliacao profissional.', subtitle
    ))

    info = [
        ['Avaliacao', assessment_id, 'Data', str(metadata.get('data', ''))],
        ['Setor', str(metadata.get('setor', '')), 'Turno', str(metadata.get('turno', ''))],
        ['Operacao / posto', str(metadata.get('operacao', '')), 'Colaborador', str(metadata.get('colaborador', ''))],
        ['Avaliador', str(metadata.get('avaliador', '')), 'Inicio / fim', f"{metadata.get('inicio','')} - {metadata.get('fim','')}"],
    ]
    t = Table(info, colWidths=[29*mm, 57*mm, 28*mm, 60*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),LIGHT), ('BACKGROUND',(2,0),(2,-1),LIGHT),
        ('TEXTCOLOR',(0,0),(-1,-1),NAVY), ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'), ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),8), ('GRID',(0,0),(-1,-1),0.45,GRID),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('LEFTPADDING',(0,0),(-1,-1),5),
        ('RIGHTPADDING',(0,0),(-1,-1),5), ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    story += [t, Spacer(1, 6*mm)]

    story.append(Paragraph('1. Resumo da medicao', h2))
    metrics = [
        ['Tempo analisado', _fmt_seconds(snapshot.get('total_time',0)), 'Exposicao geral', f"{snapshot.get('risk_pct',0):.1f}%"],
        ['Eventos ergonomicos', str(snapshot.get('events',0)), 'Maior evento', _fmt_seconds(snapshot.get('max_event_duration',0))],
        ['IRE maximo', str(snapshot.get('max_ire', snapshot.get('ire',0))), 'Evidencias salvas', str(len(evidence or []))],
    ]
    mt = Table(metrics, colWidths=[40*mm, 46*mm, 40*mm, 48*mm])
    mt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),NAVY), ('BACKGROUND',(2,0),(2,-1),NAVY),
        ('TEXTCOLOR',(0,0),(0,-1),colors.white), ('TEXTCOLOR',(2,0),(2,-1),colors.white),
        ('TEXTCOLOR',(1,0),(1,-1),NAVY), ('TEXTCOLOR',(3,0),(3,-1),NAVY),
        ('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),9),
        ('GRID',(0,0),(-1,-1),0.5,GRID), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(1,0),(1,-1),'CENTER'), ('ALIGN',(3,0),(3,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),7), ('BOTTOMPADDING',(0,0),(-1,-1),7),
    ]))
    story += [mt, Spacer(1, 4*mm)]

    exposures = [
        ['Fator', 'Exposicao', 'Eventos', 'Pico observado'],
        ['Tronco', f"{snapshot.get('trunk_pct',0):.1f}%", str(snapshot.get('factor_events',{}).get('TRONCO',0)), _fmt_angle(snapshot.get('peak_values',{}).get('TRONCO'))],
        ['Pescoco', f"{snapshot.get('neck_pct',0):.1f}%", str(snapshot.get('factor_events',{}).get('PESCOCO',0)), _fmt_angle(snapshot.get('peak_values',{}).get('PESCOCO'))],
        ['Braco elevado', f"{snapshot.get('arm_pct',0):.1f}%", str(snapshot.get('factor_events',{}).get('BRACO',0)), _fmt_angle(snapshot.get('peak_values',{}).get('BRACO'))],
        ['Flexao de joelho', f"{snapshot.get('knee_pct',0):.1f}%", str(snapshot.get('factor_events',{}).get('JOELHO',0)), _fmt_angle(snapshot.get('peak_values',{}).get('JOELHO'))],
    ]
    et = Table(exposures, colWidths=[60*mm, 36*mm, 33*mm, 45*mm])
    et.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY2), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),8.4), ('GRID',(0,0),(-1,-1),0.45,GRID),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]), ('ALIGN',(1,1),(-1,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story += [et, Spacer(1, 5*mm)]

    story.append(Paragraph('2. RULA e REBA assistidos', h2))
    rula_score = rula_result.get('score','--') if rula_result else '--'
    rula_level = rula_result.get('level','Nao calculado') if rula_result else 'Nao calculado'
    reba_score = reba_result.get('score','--') if reba_result else '--'
    reba_level = reba_result.get('level','Nao calculado') if reba_result else 'Nao calculado'

    score_data = [
        [Paragraph('<b>RULA</b>', center), Paragraph('<b>REBA</b>', center)],
        [Paragraph(f'<font size="22"><b>{rula_score}/7</b></font><br/>{rula_level}', center),
         Paragraph(f'<font size="22"><b>{reba_score}/15</b></font><br/>{reba_level}', center)],
        [Paragraph(str(rula_result.get('action','')) if rula_result else '', small),
         Paragraph(str(reba_result.get('action','')) if reba_result else '', small)],
    ]
    stbl = Table(score_data, colWidths=[87*mm,87*mm])
    stbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,0),_score_color(rula_level)),
        ('BACKGROUND',(1,0),(1,0),_score_color(reba_level)),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white), ('GRID',(0,0),(-1,-1),0.5,GRID),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('TOPPADDING',(0,0),(-1,-1),7), ('BOTTOMPADDING',(0,0),(-1,-1),7),
    ]))
    story += [stbl, Spacer(1, 4*mm)]

    if critical_pose:
        pose_rows = [
            ['Postura critica usada no fechamento', 'Valor'],
            ['Tronco', _fmt_angle(critical_pose.get('trunk'))],
            ['Pescoco', _fmt_angle(critical_pose.get('neck'))],
            ['Braco esquerdo / direito', f"{_fmt_angle(critical_pose.get('shoulder_l'))} / {_fmt_angle(critical_pose.get('shoulder_r'))}"],
            ['Cotovelo esquerdo / direito', f"{_fmt_angle(critical_pose.get('elbow_l'))} / {_fmt_angle(critical_pose.get('elbow_r'))}"],
            ['Punho esquerdo / direito', f"{_fmt_angle(critical_pose.get('wrist_l'))} / {_fmt_angle(critical_pose.get('wrist_r'))}"],
            ['Joelho esquerdo / direito', f"{_fmt_angle(critical_pose.get('knee_l'))} / {_fmt_angle(critical_pose.get('knee_r'))}"],
        ]
        pt = Table(pose_rows, colWidths=[87*mm,87*mm])
        pt.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),LIGHT), ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTNAME',(0,1),(-1,-1),'Helvetica'), ('FONTSIZE',(0,0),(-1,-1),8),
            ('GRID',(0,0),(-1,-1),0.45,GRID), ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ]))
        story += [pt, Spacer(1, 5*mm)]

    story.append(Paragraph('3. Evidencias fotograficas automaticas', h2))
    story.append(Paragraph(
        'As imagens abaixo sao capturadas automaticamente quando um fator entra em exposicao. '
        'O sistema limita capturas repetidas para evitar duplicidade e prioriza evidencias de maior severidade.', body
    ))
    story.append(Spacer(1, 3*mm))

    if not evidence:
        story.append(Paragraph('Nenhuma evidencia fotografica foi registrada durante esta sessao.', body))
    else:
        factor_order = ['TRONCO','PESCOCO','BRACO','JOELHO']
        labels = {'TRONCO':'Tronco','PESCOCO':'Pescoco','BRACO':'Braco elevado','JOELHO':'Flexao de joelho'}
        for factor in factor_order:
            items = [e for e in evidence if e.get('factor') == factor]
            if not items:
                continue
            story.append(Paragraph(labels[factor], h2))
            for e in items[:6]:
                path = Path(e.get('path',''))
                if not path.exists():
                    continue
                caption = (
                    f"Horario: {e.get('clock','')} | Tempo: {_fmt_seconds(e.get('elapsed',0))} | "
                    f"Valor: {_fmt_angle(e.get('value'))} | Risco: {e.get('risk','')}"
                )
                img = Image(str(path))
                max_w, max_h = 170*mm, 95*mm
                ratio = min(max_w / img.imageWidth, max_h / img.imageHeight)
                img.drawWidth = img.imageWidth * ratio
                img.drawHeight = img.imageHeight * ratio
                block = [img, Spacer(1, 1.5*mm), Paragraph(caption, small), Spacer(1, 4*mm)]
                story.append(KeepTogether(block))

    story.append(PageBreak())
    story.append(Paragraph('4. Interpretacao e observacoes', h2))

    ranked = [
        ('Tronco', float(snapshot.get('trunk_pct',0))),
        ('Pescoco', float(snapshot.get('neck_pct',0))),
        ('Braco elevado', float(snapshot.get('arm_pct',0))),
        ('Flexao de joelho', float(snapshot.get('knee_pct',0))),
    ]
    ranked.sort(key=lambda x: x[1], reverse=True)
    top = ', '.join(f'{name} ({pct:.1f}%)' for name,pct in ranked[:2])

    story.append(Paragraph(
        f'Os fatores com maior exposicao acumulada nesta medicao foram: <b>{top}</b>. '
        'A interpretacao deve considerar o ciclo real, variabilidade da tarefa, ritmo, pausas, forca/carga, '
        'condicoes ambientais, organizacao do trabalho e a percepcao do trabalhador.', body
    ))
    story.append(Spacer(1, 4*mm))

    obs = str(metadata.get('observacao','') or '').strip()
    if obs:
        story.append(Paragraph('<b>Observacao do avaliador:</b>', body))
        story.append(Paragraph(obs.replace('\n','<br/>'), body))
        story.append(Spacer(1, 4*mm))

    story.append(Paragraph('<b>Nota metodologica</b>', h2))
    story.append(Paragraph(
        'O IRE e um indicador experimental interno deste MVP. RULA e REBA sao metodos observacionais de triagem. '
        'Nesta implementacao, angulos corporais 2D sao obtidos por visao computacional e fatores nao inferidos com '
        'seguranca pela camera sao informados pelo avaliador. O documento nao declara conformidade automatica com a NR-17.', body
    ))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return pdf_path


import csv
import html
import threading
import time
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
import shutil

import av
import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer


# ============================================================
# CONFIGURAÇÃO
# ============================================================
APP_TITLE = "NR-17 | Ergonomia por Visão"
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "pose_landmarker_lite.task"
HISTORY_PATH = BASE_DIR / "historico_nr17.csv"
EVIDENCE_ROOT = BASE_DIR / "evidencias_nr17"
REPORT_ROOT = BASE_DIR / "relatorios_nr17"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/latest/"
    "pose_landmarker_lite.task"
)


# Perfis pensados para WebRTC/Streamlit Cloud.
# A captura/evidência usa a resolução entregue pelo navegador.
# O MediaPipe processa uma cópia reduzida para preservar FPS e estabilidade.
CAMERA_PROFILES = {
    "Industrial · 1280×720 · 30 FPS": {
        "width": 1280, "height": 720, "fps": 30, "process_long_side": 960,
    },
    "Alta precisão · 1920×1080 · 24 FPS": {
        "width": 1920, "height": 1080, "fps": 24, "process_long_side": 960,
    },
    "Econômica · 960×540 · 30 FPS": {
        "width": 960, "height": 540, "fps": 30, "process_long_side": 640,
    },
}

# Landmarks MediaPipe Pose
L_EAR, R_EAR = 7, 8
L_SHOULDER, R_SHOULDER = 11, 12
L_ELBOW, R_ELBOW = 13, 14
L_WRIST, R_WRIST = 15, 16
L_PINKY, R_PINKY = 17, 18
L_INDEX, R_INDEX = 19, 20
L_HIP, R_HIP = 23, 24
L_KNEE, R_KNEE = 25, 26
L_ANKLE, R_ANKLE = 27, 28

POSE_CONNECTIONS = [
    (7, 11), (8, 12), (11, 12),
    (11, 13), (13, 15), (15, 17), (15, 19),
    (12, 14), (14, 16), (16, 18), (16, 20),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (25, 27), (24, 26), (26, 28),
]


# ============================================================
# TABELAS RULA
# ============================================================
# Table A: linhas = upper arm 1..6 / lower arm 1..3
# colunas = wrist 1..4 / wrist twist 1..2
RULA_TABLE_A = [
    [1,2,2,2,2,3,3,3],
    [2,2,2,2,3,3,3,3],
    [2,3,3,3,3,3,4,4],

    [2,3,3,3,3,4,4,4],
    [2,3,3,3,3,3,4,4],
    [3,4,4,4,4,4,5,5],

    [3,3,4,4,4,4,5,5],
    [3,4,4,4,4,4,5,5],
    [4,4,4,4,4,5,5,5],

    [4,4,4,4,4,5,5,5],
    [4,4,4,4,4,5,5,5],
    [4,4,4,5,5,5,6,6],

    [5,5,5,5,5,6,6,7],
    [5,6,6,6,6,6,7,7],
    [6,6,6,7,7,7,7,8],

    [7,7,7,7,7,8,8,9],
    [8,8,8,8,8,9,9,9],
    [9,9,9,9,9,9,9,9],
]

# Table B: linhas neck 1..6
# colunas = trunk 1..6 / legs 1..2
RULA_TABLE_B = [
    [1,3,2,3,3,4,5,5,6,6,7,7],
    [2,3,2,3,4,5,5,5,6,7,7,7],
    [3,3,3,4,4,5,5,6,6,7,7,7],
    [5,5,5,6,6,7,7,7,7,7,8,8],
    [7,7,7,7,7,8,8,8,8,8,8,8],
    [8,8,8,8,8,8,8,9,9,9,9,9],
]

# Table C: linhas final A 1..8+, colunas final B 1..7+
RULA_TABLE_C = [
    [1,2,3,3,4,5,5],
    [2,2,3,4,4,5,5],
    [3,3,3,4,4,5,6],
    [3,3,3,4,5,6,6],
    [4,4,4,5,6,7,7],
    [4,4,5,6,6,7,7],
    [5,5,6,6,7,7,7],
    [5,5,6,7,7,7,7],
]


# ============================================================
# TABELAS REBA
# ============================================================
# Table A: linhas trunk 1..5
# colunas = neck 1..3 / legs 1..4
REBA_TABLE_A = [
    [1,2,3,4, 1,2,3,4, 3,3,5,6],
    [2,3,4,5, 3,4,5,6, 4,5,6,7],
    [2,4,5,6, 4,5,6,7, 5,6,7,8],
    [3,5,6,7, 5,6,7,8, 6,7,8,9],
    [4,6,7,8, 6,7,8,9, 7,8,9,9],
]

# Table B: linhas upper arm 1..6
# colunas = lower arm 1..2 / wrist 1..3
REBA_TABLE_B = [
    [1,2,2, 1,2,3],
    [1,2,3, 2,3,4],
    [3,4,5, 4,5,5],
    [4,5,5, 5,6,7],
    [6,7,8, 7,8,8],
    [7,8,8, 8,9,9],
]

# Table C: linhas Score A 1..12, colunas Score B 1..12
REBA_TABLE_C = [
    [1,1,1,2,3,3,4,5,6,7,7,7],
    [1,2,2,3,4,4,5,6,6,7,7,8],
    [2,3,3,3,4,5,6,7,7,8,8,8],
    [3,4,4,4,5,6,7,8,8,9,9,9],
    [4,4,4,5,6,7,8,8,9,9,9,9],
    [6,6,6,7,8,8,9,9,10,10,10,10],
    [7,7,7,8,9,9,9,10,10,11,11,11],
    [8,8,8,9,10,10,10,10,10,11,11,11],
    [9,9,9,10,10,10,11,11,11,12,12,12],
    [10,10,10,11,11,11,11,12,12,12,12,12],
    [11,11,11,11,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12],
]


# ============================================================
# ESTADO
# ============================================================
def init_state():
    defaults = {
        "assessment_id": uuid.uuid4().hex[:8].upper(),
        "assessment_started": datetime.now(),
        "setor": "",
        "operacao": "",
        "colaborador": "",
        "turno": "1º Turno",
        "avaliador": "",
        "observacao": "",
        "captured_pose": None,
        "saved_message": "",
        "final_pdf": None,
        "max_rula_live": 0,
        "max_reba_live": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ============================================================
# FUNÇÕES GERAIS
# ============================================================
def ensure_model():
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
        return True, None
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        return True, None
    except Exception as exc:
        return False, str(exc)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def pxy(landmarks, idx):
    lm = landmarks[idx]
    return np.array([float(lm.x), float(lm.y)], dtype=np.float32)


def visible(landmarks, idx, min_visibility=0.45):
    lm = landmarks[idx]
    vis = float(getattr(lm, "visibility", 1.0) or 0.0)
    pres = float(getattr(lm, "presence", 1.0) or 0.0)
    return vis >= min_visibility and pres >= min_visibility


def midpoint(landmarks, a, b):
    return (pxy(landmarks, a) + pxy(landmarks, b)) / 2.0


def angle3(a, b, c):
    ba = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    bc = np.asarray(c, dtype=float) - np.asarray(b, dtype=float)
    den = np.linalg.norm(ba) * np.linalg.norm(bc)
    if den < 1e-9:
        return None
    val = np.clip(np.dot(ba, bc) / den, -1.0, 1.0)
    return float(np.degrees(np.arccos(val)))


def vector_angle(v1, v2):
    v1 = np.asarray(v1, dtype=float)
    v2 = np.asarray(v2, dtype=float)
    den = np.linalg.norm(v1) * np.linalg.norm(v2)
    if den < 1e-9:
        return None
    val = np.clip(np.dot(v1, v2) / den, -1.0, 1.0)
    return float(np.degrees(np.arccos(val)))


def fmt_seconds(seconds):
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def fmt_angle(value):
    return "--" if value is None else f"{value:.1f}°"


def safe(value, fallback="Não informado"):
    text = str(value or "").strip()
    return html.escape(text if text else fallback)


def trunk_angle(landmarks):
    sm = midpoint(landmarks, L_SHOULDER, R_SHOULDER)
    hm = midpoint(landmarks, L_HIP, R_HIP)
    return vector_angle(sm - hm, np.array([0.0, -1.0]))


def neck_angle(landmarks):
    sm = midpoint(landmarks, L_SHOULDER, R_SHOULDER)
    hm = midpoint(landmarks, L_HIP, R_HIP)
    em = midpoint(landmarks, L_EAR, R_EAR)
    return vector_angle(em - sm, sm - hm)


def shoulder_angle(landmarks, hip, shoulder, elbow):
    return angle3(pxy(landmarks, hip), pxy(landmarks, shoulder), pxy(landmarks, elbow))


def elbow_angle(landmarks, shoulder, elbow, wrist):
    return angle3(pxy(landmarks, shoulder), pxy(landmarks, elbow), pxy(landmarks, wrist))


def knee_angle(landmarks, hip, knee, ankle):
    return angle3(pxy(landmarks, hip), pxy(landmarks, knee), pxy(landmarks, ankle))


def wrist_deviation_angle(landmarks, elbow, wrist, index, pinky):
    hand = (pxy(landmarks, index) + pxy(landmarks, pinky)) / 2.0
    internal = angle3(pxy(landmarks, elbow), pxy(landmarks, wrist), hand)
    if internal is None:
        return None
    return abs(180.0 - internal)


def calc_ire(values, cfg):
    trunk = values.get("trunk") or 0
    neck = values.get("neck") or 0
    arm = max([x for x in [values.get("shoulder_l"), values.get("shoulder_r")] if x is not None] or [0])
    knee = min([x for x in [values.get("knee_l"), values.get("knee_r")] if x is not None] or [180])

    s_trunk = clamp(trunk / max(cfg["trunk_limit"] * 2, 1) * 100, 0, 100)
    s_neck = clamp(neck / max(cfg["neck_limit"] * 2, 1) * 100, 0, 100)
    s_arm = clamp(arm / max(cfg["arm_limit"] * 1.8, 1) * 100, 0, 100)
    s_knee = 0 if knee >= cfg["knee_limit"] else clamp(
        (cfg["knee_limit"] - knee) / max(cfg["knee_limit"] - 70, 1) * 100, 0, 100
    )
    return int(round(0.35*s_trunk + 0.20*s_neck + 0.25*s_arm + 0.20*s_knee))


def risk_label(n_flags):
    return ["BAIXO", "ATENÇÃO", "ALTO", "CRÍTICO"][min(max(n_flags, 0), 3)]


# ============================================================
# RULA
# ============================================================
def rula_upper_arm_score(angle, shoulder_raised=False, abducted=False, supported=False):
    a = abs(float(angle or 0))
    if a <= 20:
        score = 1
    elif a <= 45:
        score = 2
    elif a <= 90:
        score = 3
    else:
        score = 4
    score += int(shoulder_raised) + int(abducted) - int(supported)
    return clamp(score, 1, 6)


def rula_lower_arm_score(elbow, across=False):
    if elbow is None:
        score = 1
    else:
        score = 1 if 60 <= elbow <= 100 else 2
    score += int(across)
    return clamp(score, 1, 3)


def rula_wrist_score(wrist_deg, bent_midline=False):
    a = abs(float(wrist_deg or 0))
    if a < 1:
        score = 1
    elif a <= 15:
        score = 2
    else:
        score = 3
    score += int(bent_midline)
    return clamp(score, 1, 4)


def rula_neck_score(angle, extension=False, twisted=False, side_bent=False):
    a = abs(float(angle or 0))
    if extension:
        score = 4
    elif a <= 10:
        score = 1
    elif a <= 20:
        score = 2
    else:
        score = 3
    score += int(twisted) + int(side_bent)
    return clamp(score, 1, 6)


def rula_trunk_score(angle, twisted=False, side_bent=False):
    a = abs(float(angle or 0))
    if a < 1:
        score = 1
    elif a <= 20:
        score = 2
    elif a <= 60:
        score = 3
    else:
        score = 4
    score += int(twisted) + int(side_bent)
    return clamp(score, 1, 6)


def calculate_rula(pose, opts):
    side = opts["side"]
    if side == "Esquerdo":
        ua_angle = pose.get("shoulder_l")
        la_angle = pose.get("elbow_l")
        wrist_angle = pose.get("wrist_l")
    else:
        ua_angle = pose.get("shoulder_r")
        la_angle = pose.get("elbow_r")
        wrist_angle = pose.get("wrist_r")

    ua = rula_upper_arm_score(
        ua_angle,
        opts["shoulder_raised"],
        opts["abducted"],
        opts["arm_supported"],
    )
    la = rula_lower_arm_score(la_angle, opts["across"])
    wr = rula_wrist_score(wrist_angle, opts["wrist_midline"])
    wt = 2 if opts["wrist_twist_extreme"] else 1

    row_a = (ua - 1) * 3 + (la - 1)
    col_a = (wr - 1) * 2 + (wt - 1)
    table_a = RULA_TABLE_A[row_a][col_a]

    ne = rula_neck_score(
        pose.get("neck"),
        opts["neck_extension"],
        opts["neck_twisted"],
        opts["neck_side"],
    )
    tr = rula_trunk_score(
        pose.get("trunk"),
        opts["trunk_twisted"],
        opts["trunk_side"],
    )
    legs = 1 if opts["legs_supported"] else 2

    row_b = ne - 1
    col_b = (tr - 1) * 2 + (legs - 1)
    table_b = RULA_TABLE_B[row_b][col_b]

    final_a = clamp(table_a + opts["muscle_use"] + opts["force_score"], 1, 8)
    final_b = clamp(table_b + opts["muscle_use"] + opts["force_score"], 1, 7)
    final = RULA_TABLE_C[final_a - 1][final_b - 1]

    if final <= 2:
        level = "Aceitável"
        action = "Postura aceitável se não mantida/repetida por períodos prolongados."
    elif final <= 4:
        level = "Investigar"
        action = "Investigar mais; mudanças podem ser necessárias."
    elif final <= 6:
        level = "Ação em breve"
        action = "Investigar e implementar mudanças em curto prazo."
    else:
        level = "Ação imediata"
        action = "Investigar e implementar mudanças imediatamente."

    return {
        "score": final,
        "level": level,
        "action": action,
        "A": table_a,
        "B": table_b,
        "final_a": final_a,
        "final_b": final_b,
        "upper_arm": ua,
        "lower_arm": la,
        "wrist": wr,
        "wrist_twist": wt,
        "neck": ne,
        "trunk": tr,
        "legs": legs,
    }


# ============================================================
# REBA
# ============================================================
def reba_trunk_score(angle, twisted_or_side=False):
    a = abs(float(angle or 0))
    if a < 1:
        score = 1
    elif a <= 20:
        score = 2
    elif a <= 60:
        score = 3
    else:
        score = 4
    score += int(twisted_or_side)
    return clamp(score, 1, 5)


def reba_neck_score(angle, extension=False, twisted_or_side=False):
    a = abs(float(angle or 0))
    score = 2 if extension or a > 20 else 1
    score += int(twisted_or_side)
    return clamp(score, 1, 3)


def reba_leg_score(knee_internal_angle, bilateral=True, seated=False):
    score = 1 if bilateral else 2
    if seated:
        return score
    if knee_internal_angle is not None:
        flexion = max(0.0, 180.0 - knee_internal_angle)
        if 30 <= flexion <= 60:
            score += 1
        elif flexion > 60:
            score += 2
    return clamp(score, 1, 4)


def reba_upper_arm_score(angle, shoulder_raised=False, abducted=False, supported=False):
    a = abs(float(angle or 0))
    if a <= 20:
        score = 1
    elif a <= 45:
        score = 2
    elif a <= 90:
        score = 3
    else:
        score = 4
    if shoulder_raised:
        score += 1
    if abducted:
        score += 1
    if supported:
        score -= 1
    return clamp(score, 1, 6)


def reba_lower_arm_score(elbow):
    if elbow is None:
        return 1
    return 1 if 60 <= elbow <= 100 else 2


def reba_wrist_score(wrist_deg, twisted=False):
    score = 1 if abs(float(wrist_deg or 0)) <= 15 else 2
    score += int(twisted)
    return clamp(score, 1, 3)


def calculate_reba(pose, opts):
    side = opts["side"]
    if side == "Esquerdo":
        ua_angle = pose.get("shoulder_l")
        la_angle = pose.get("elbow_l")
        wrist_angle = pose.get("wrist_l")
        knee = pose.get("knee_l")
    else:
        ua_angle = pose.get("shoulder_r")
        la_angle = pose.get("elbow_r")
        wrist_angle = pose.get("wrist_r")
        knee = pose.get("knee_r")

    tr = reba_trunk_score(
        pose.get("trunk"),
        opts["trunk_twisted"] or opts["trunk_side"],
    )
    ne = reba_neck_score(
        pose.get("neck"),
        opts["neck_extension"],
        opts["neck_twisted"] or opts["neck_side"],
    )
    legs = reba_leg_score(
        knee,
        bilateral=opts["legs_supported"],
        seated=opts["seated"],
    )

    col_a = (ne - 1) * 4 + (legs - 1)
    posture_a = REBA_TABLE_A[tr - 1][col_a]

    load = opts["load_score"] + int(opts["shock_force"])
    load = clamp(load, 0, 3)
    score_a = clamp(posture_a + load, 1, 12)

    ua = reba_upper_arm_score(
        ua_angle,
        opts["shoulder_raised"],
        opts["abducted"],
        opts["arm_supported"],
    )
    la = reba_lower_arm_score(la_angle)
    wr = reba_wrist_score(wrist_angle, opts["wrist_twisted"])

    col_b = (la - 1) * 3 + (wr - 1)
    posture_b = REBA_TABLE_B[ua - 1][col_b]
    score_b = clamp(posture_b + opts["coupling_score"], 1, 12)

    score_c = REBA_TABLE_C[score_a - 1][score_b - 1]
    activity = (
        int(opts["static_posture"])
        + int(opts["repetition"])
        + int(opts["rapid_changes"])
    )
    final = clamp(score_c + activity, 1, 15)

    if final == 1:
        level, action = "Negligível", "Nenhuma ação necessária."
    elif final <= 3:
        level, action = "Baixo", "Mudança pode ser necessária."
    elif final <= 7:
        level, action = "Médio", "Investigar; mudança necessária."
    elif final <= 10:
        level, action = "Alto", "Investigar e implementar mudança em curto prazo."
    else:
        level, action = "Muito alto", "Intervenção imediata."

    return {
        "score": final,
        "level": level,
        "action": action,
        "posture_a": posture_a,
        "score_a": score_a,
        "posture_b": posture_b,
        "score_b": score_b,
        "score_c": score_c,
        "activity": activity,
        "trunk": tr,
        "neck": ne,
        "legs": legs,
        "upper_arm": ua,
        "lower_arm": la,
        "wrist": wr,
    }



# ============================================================
# HISTÓRICO / EVIDÊNCIAS / RELATÓRIO
# ============================================================
def assessment_evidence_dir(assessment_id):
    path = EVIDENCE_ROOT / str(assessment_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def assessment_report_path(assessment_id):
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    return REPORT_ROOT / f"relatorio_ergonomia_{assessment_id}.pdf"


def save_record(snapshot, rula_result=None, reba_result=None, pdf_path=None):
    row = {
        "avaliacao_id": st.session_state.assessment_id,
        "inicio": st.session_state.assessment_started.strftime("%Y-%m-%d %H:%M:%S"),
        "fim": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "setor": st.session_state.setor,
        "operacao": st.session_state.operacao,
        "colaborador": st.session_state.colaborador,
        "turno": st.session_state.turno,
        "avaliador": st.session_state.avaliador,
        "observacao": st.session_state.observacao,
        "tempo_analisado_s": round(snapshot.get("total_time", 0), 1),
        "exposicao_geral_pct": round(snapshot.get("risk_pct", 0), 1),
        "eventos": int(snapshot.get("events", 0)),
        "maior_evento_s": round(snapshot.get("max_event_duration", 0), 1),
        "exposicao_tronco_pct": round(snapshot.get("trunk_pct", 0), 1),
        "exposicao_pescoco_pct": round(snapshot.get("neck_pct", 0), 1),
        "exposicao_braco_pct": round(snapshot.get("arm_pct", 0), 1),
        "exposicao_joelho_pct": round(snapshot.get("knee_pct", 0), 1),
        "eventos_tronco": snapshot.get("factor_events", {}).get("TRONCO", 0),
        "eventos_pescoco": snapshot.get("factor_events", {}).get("PESCOCO", 0),
        "eventos_braco": snapshot.get("factor_events", {}).get("BRACO", 0),
        "eventos_joelho": snapshot.get("factor_events", {}).get("JOELHO", 0),
        "ire_maximo": snapshot.get("max_ire", 0),
        "evidencias": len(snapshot.get("evidence", [])),
        "rula": rula_result.get("score") if rula_result else "",
        "rula_nivel": rula_result.get("level") if rula_result else "",
        "reba": reba_result.get("score") if reba_result else "",
        "reba_nivel": reba_result.get("level") if reba_result else "",
        "pdf": str(pdf_path or ""),
    }

    exists = HISTORY_PATH.exists()
    with HISTORY_PATH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys(), delimiter=";")
        if not exists:
            writer.writeheader()
        writer.writerow(row)
    return HISTORY_PATH


def default_rula_opts():
    return {
        "side": "Direito",
        "shoulder_raised": False,
        "abducted": False,
        "arm_supported": False,
        "across": False,
        "wrist_midline": False,
        "wrist_twist_extreme": False,
        "neck_extension": False,
        "neck_twisted": False,
        "neck_side": False,
        "trunk_twisted": False,
        "trunk_side": False,
        "legs_supported": True,
        "muscle_use": 0,
        "force_score": 0,
    }


def default_reba_opts():
    return {
        "side": "Direito",
        "shoulder_raised": False,
        "abducted": False,
        "arm_supported": False,
        "neck_extension": False,
        "neck_twisted": False,
        "neck_side": False,
        "trunk_twisted": False,
        "trunk_side": False,
        "legs_supported": True,
        "seated": False,
        "wrist_twisted": False,
        "load_score": 0,
        "shock_force": False,
        "coupling_score": 0,
        "static_posture": False,
        "repetition": False,
        "rapid_changes": False,
    }



# ============================================================
# MVP 04 - RECURSOS AVANÇADOS
# ============================================================
from collections import deque
import json
import pandas as pd

HISTORY_PATH_V4 = BASE_DIR / "historico_nr17_v4.csv"
ACTION_ROOT = BASE_DIR / "planos_acao_nr17"
ACTION_ROOT.mkdir(parents=True, exist_ok=True)

# Pontos usados para verificar se o corpo está suficientemente visível
QUALITY_LANDMARKS = [
    L_EAR, R_EAR,
    L_SHOULDER, R_SHOULDER,
    L_ELBOW, R_ELBOW,
    L_WRIST, R_WRIST,
    L_HIP, R_HIP,
    L_KNEE, R_KNEE,
    L_ANKLE, R_ANKLE,
]


def _percent_dict(seconds_dict, total):
    total = float(total or 0)
    if total <= 0:
        return {int(k): 0.0 for k in seconds_dict}
    return {int(k): 100.0 * float(v) / total for k, v in seconds_dict.items()}


def _dominant_score(seconds_dict):
    if not seconds_dict or sum(seconds_dict.values()) <= 0:
        return 0
    return int(max(seconds_dict, key=lambda k: seconds_dict[k]))


def _weighted_score(seconds_dict):
    total = sum(seconds_dict.values())
    if total <= 0:
        return 0.0
    return sum(float(k) * float(v) for k, v in seconds_dict.items()) / total


def _rula_group_distribution(seconds_dict):
    total = sum(seconds_dict.values())
    groups = {"1-2": 0.0, "3-4": 0.0, "5-6": 0.0, "7": 0.0}
    for score, seconds in seconds_dict.items():
        if score <= 2:
            groups["1-2"] += seconds
        elif score <= 4:
            groups["3-4"] += seconds
        elif score <= 6:
            groups["5-6"] += seconds
        else:
            groups["7"] += seconds
    if total:
        groups = {k: 100*v/total for k, v in groups.items()}
    return groups


def _reba_group_distribution(seconds_dict):
    total = sum(seconds_dict.values())
    groups = {"1": 0.0, "2-3": 0.0, "4-7": 0.0, "8-10": 0.0, "11-15": 0.0}
    for score, seconds in seconds_dict.items():
        if score <= 1:
            groups["1"] += seconds
        elif score <= 3:
            groups["2-3"] += seconds
        elif score <= 7:
            groups["4-7"] += seconds
        elif score <= 10:
            groups["8-10"] += seconds
        else:
            groups["11-15"] += seconds
    if total:
        groups = {k: 100*v/total for k, v in groups.items()}
    return groups


def _quality_label(score):
    score = float(score or 0)
    if score >= 85:
        return "EXCELENTE"
    if score >= 70:
        return "BOA"
    if score >= 55:
        return "ATENÇÃO"
    return "INADEQUADA"


def _quality_color(score):
    score = float(score or 0)
    if score >= 85:
        return "#3DDC97"
    if score >= 70:
        return "#7EE081"
    if score >= 55:
        return "#F4C95D"
    return "#FF6B6B"


def _safe_num(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _metric_row(label, value):
    return [Paragraph(f"<b>{label}</b>", _PDF_BODY), Paragraph(str(value), _PDF_BODY)]


# ============================================================
# PDF EXECUTIVO V4
# ============================================================
_PDF_STYLES = getSampleStyleSheet()
_PDF_TITLE = ParagraphStyle(
    "V4Title", parent=_PDF_STYLES["Title"], fontName="Helvetica-Bold",
    fontSize=19, leading=22, textColor=NAVY, spaceAfter=4,
)
_PDF_H2 = ParagraphStyle(
    "V4H2", parent=_PDF_STYLES["Heading2"], fontName="Helvetica-Bold",
    fontSize=11.5, leading=14, textColor=NAVY, spaceBefore=6, spaceAfter=6,
)
_PDF_BODY = ParagraphStyle(
    "V4Body", parent=_PDF_STYLES["BodyText"], fontName="Helvetica",
    fontSize=8.3, leading=11, textColor=NAVY,
)
_PDF_SMALL = ParagraphStyle(
    "V4Small", parent=_PDF_BODY, fontSize=7.2, leading=9.5, textColor=MID,
)
_PDF_CENTER = ParagraphStyle(
    "V4Center", parent=_PDF_BODY, alignment=TA_CENTER,
)


def _pdf_table(data, widths, header=True, font_size=8):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [
        ("GRID", (0,0), (-1,-1), 0.45, GRID),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTSIZE", (0,0), (-1,-1), font_size),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0,0), (-1,0), NAVY2),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
        ]
    t.setStyle(TableStyle(cmds))
    return t


def generate_nr17_pdf(
    pdf_path, metadata, snapshot, rula_result, reba_result,
    evidence, critical_pose=None, cycles=None, actions=None,
):
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cycles = cycles or []
    actions = actions or []
    evidence = evidence or []

    assessment_id = str(metadata.get("avaliacao_id", ""))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(GRID)
        canvas.line(17*mm, 14*mm, A4[0]-17*mm, 14*mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MID)
        canvas.drawString(17*mm, 9*mm, f"Ergonomia por Visao | Avaliacao {assessment_id}")
        canvas.drawRightString(A4[0]-17*mm, 9*mm, f"Pagina {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        rightMargin=17*mm, leftMargin=17*mm,
        topMargin=16*mm, bottomMargin=18*mm,
        title=f"Relatorio de Ergonomia {assessment_id}",
        author=str(metadata.get("avaliador", "") or "Sistema Ergonomia por Visao"),
    )

    story = []
    story.append(Paragraph("RELATÓRIO DE ACOMPANHAMENTO ERGONÔMICO", _PDF_TITLE))
    story.append(Paragraph(
        "Visão computacional + tempo de exposição + RULA/REBA assistidos + evidências automáticas. "
        "Ferramenta de apoio técnico; não substitui AEP, AET ou avaliação profissional.",
        _PDF_SMALL,
    ))
    story.append(Spacer(1, 3*mm))

    info = [
        ["Avaliação", assessment_id, "Data", metadata.get("data","")],
        ["Setor", metadata.get("setor",""), "Turno", metadata.get("turno","")],
        ["Operação / posto", metadata.get("operacao",""), "Colaborador", metadata.get("colaborador","")],
        ["Avaliador", metadata.get("avaliador",""), "Início / fim", f"{metadata.get('inicio','')} - {metadata.get('fim','')}"],
        ["Modo de captura", metadata.get("capture_mode",""), "Marcador", metadata.get("marker_info","")],
    ]
    story += [_pdf_table(info, [29*mm,57*mm,29*mm,59*mm], header=False), Spacer(1,4*mm)]

    story.append(Paragraph("1. Resumo executivo", _PDF_H2))
    quality_avg = snapshot.get("quality_avg", 0)
    summary = [
        ["Indicador", "Resultado", "Indicador", "Resultado"],
        ["Tempo válido", _fmt_seconds(snapshot.get("total_time",0)), "Exposição geral", f"{snapshot.get('risk_pct',0):.1f}%"],
        ["IRE máximo", str(snapshot.get("max_ire",0)), "Eventos", str(snapshot.get("events",0))],
        ["RULA pior / predominante", f"{snapshot.get('max_rula',0)}/7 | {snapshot.get('rula_dominant',0)}", "REBA pior / predominante", f"{snapshot.get('max_reba',0)}/15 | {snapshot.get('reba_dominant',0)}"],
        ["Qualidade média", f"{quality_avg:.1f}% ({_quality_label(quality_avg)})", "Frames válidos", f"{snapshot.get('valid_pct',0):.1f}%"],
        ["Ciclos registrados", str(len(cycles)), "Evidências", str(len(evidence))],
    ]
    story += [_pdf_table(summary, [43*mm,44*mm,43*mm,44*mm]), Spacer(1,4*mm)]

    exp_rows = [
        ["Fator", "Exposição", "Eventos", "Pico"],
        ["Tronco", f"{snapshot.get('trunk_pct',0):.1f}%", snapshot.get("factor_events",{}).get("TRONCO",0), _fmt_angle(snapshot.get("peak_values",{}).get("TRONCO"))],
        ["Pescoço", f"{snapshot.get('neck_pct',0):.1f}%", snapshot.get("factor_events",{}).get("PESCOCO",0), _fmt_angle(snapshot.get("peak_values",{}).get("PESCOCO"))],
        ["Braço elevado", f"{snapshot.get('arm_pct',0):.1f}%", snapshot.get("factor_events",{}).get("BRACO",0), _fmt_angle(snapshot.get("peak_values",{}).get("BRACO"))],
        ["Flexão de joelho", f"{snapshot.get('knee_pct',0):.1f}%", snapshot.get("factor_events",{}).get("JOELHO",0), _fmt_angle(snapshot.get("peak_values",{}).get("JOELHO"))],
    ]
    story += [_pdf_table(exp_rows, [60*mm,38*mm,34*mm,42*mm]), Spacer(1,4*mm)]

    story.append(Paragraph("2. Qualidade e confiabilidade da captura", _PDF_H2))
    quality_rows = [
        ["Critério", "Resultado"],
        ["Qualidade média da sessão", f"{quality_avg:.1f}% - {_quality_label(quality_avg)}"],
        ["Menor qualidade observada", f"{snapshot.get('quality_min',0):.1f}%"],
        ["Tempo válido / tempo descartado", f"{_fmt_seconds(snapshot.get('total_time',0))} / {_fmt_seconds(snapshot.get('invalid_time',0))}"],
        ["Cobertura corporal atual", f"{snapshot.get('coverage',0):.1f}%"],
        ["FPS estimado", f"{snapshot.get('fps',0):.1f}"],
        ["Resolução recebida / solicitada", f"{snapshot.get('resolution','--')} / {snapshot.get('requested_resolution','--')}"],
        ["Resolução usada pela IA", snapshot.get("processing_resolution","--")],
        ["Orientação", snapshot.get("orientation","--")],
        ["Marcador alvo detectado", "SIM" if snapshot.get("marker_found") else ("N/A" if metadata.get("capture_mode") == "Visão normal" else "NÃO")],
    ]
    story += [_pdf_table(quality_rows, [88*mm,86*mm]), Spacer(1,4*mm)]

    story.append(Paragraph("3. RULA / REBA no tempo", _PDF_H2))
    rula_groups = _rula_group_distribution(snapshot.get("rula_seconds",{}))
    reba_groups = _reba_group_distribution(snapshot.get("reba_seconds",{}))
    dist = [
        ["RULA", "% tempo", "REBA", "% tempo"],
        ["1-2", f"{rula_groups['1-2']:.1f}%", "1", f"{reba_groups['1']:.1f}%"],
        ["3-4", f"{rula_groups['3-4']:.1f}%", "2-3", f"{reba_groups['2-3']:.1f}%"],
        ["5-6", f"{rula_groups['5-6']:.1f}%", "4-7", f"{reba_groups['4-7']:.1f}%"],
        ["7", f"{rula_groups['7']:.1f}%", "8-10", f"{reba_groups['8-10']:.1f}%"],
        ["", "", "11-15", f"{reba_groups['11-15']:.1f}%"],
    ]
    story += [_pdf_table(dist, [44*mm,43*mm,44*mm,43*mm]), Spacer(1,3*mm)]
    story.append(Paragraph(
        f"RULA médio ponderado: <b>{snapshot.get('rula_weighted',0):.2f}</b> | "
        f"Tempo RULA ≥ 5: <b>{snapshot.get('rula_high_pct',0):.1f}%</b> | "
        f"REBA médio ponderado: <b>{snapshot.get('reba_weighted',0):.2f}</b> | "
        f"Tempo REBA ≥ 8: <b>{snapshot.get('reba_high_pct',0):.1f}%</b>.",
        _PDF_BODY,
    ))
    story.append(Spacer(1,4*mm))

    final_rows = [
        ["Método", "Fechamento", "Nível", "Conduta"],
        ["RULA", f"{rula_result.get('score','--')}/7" if rula_result else "--", rula_result.get("level","") if rula_result else "", rula_result.get("action","") if rula_result else ""],
        ["REBA", f"{reba_result.get('score','--')}/15" if reba_result else "--", reba_result.get("level","") if reba_result else "", reba_result.get("action","") if reba_result else ""],
    ]
    story += [_pdf_table(final_rows, [27*mm,31*mm,38*mm,78*mm], font_size=7.5), Spacer(1,4*mm)]

    if critical_pose:
        pose_rows = [
            ["Postura crítica / referência", "Valor"],
            ["Tronco", _fmt_angle(critical_pose.get("trunk"))],
            ["Pescoço", _fmt_angle(critical_pose.get("neck"))],
            ["Braço E / D", f"{_fmt_angle(critical_pose.get('shoulder_l'))} / {_fmt_angle(critical_pose.get('shoulder_r'))}"],
            ["Cotovelo E / D", f"{_fmt_angle(critical_pose.get('elbow_l'))} / {_fmt_angle(critical_pose.get('elbow_r'))}"],
            ["Punho E / D", f"{_fmt_angle(critical_pose.get('wrist_l'))} / {_fmt_angle(critical_pose.get('wrist_r'))}"],
            ["Joelho E / D", f"{_fmt_angle(critical_pose.get('knee_l'))} / {_fmt_angle(critical_pose.get('knee_r'))}"],
        ]
        story += [_pdf_table(pose_rows, [88*mm,86*mm]), Spacer(1,4*mm)]

    if cycles:
        story.append(Paragraph("4. Ciclos observados", _PDF_H2))
        cycle_rows = [["Ciclo","Duração","Exposição","RULA máx.","REBA máx.","Tronco","Braço"]]
        for c in cycles[:25]:
            cycle_rows.append([
                c.get("cycle", ""),
                _fmt_seconds(c.get("duration",0)),
                f"{c.get('risk_pct',0):.1f}%",
                c.get("max_rula",0),
                c.get("max_reba",0),
                f"{c.get('trunk_pct',0):.1f}%",
                f"{c.get('arm_pct',0):.1f}%",
            ])
        story += [_pdf_table(cycle_rows, [18*mm,27*mm,26*mm,25*mm,26*mm,26*mm,26*mm], font_size=7.2), Spacer(1,4*mm)]

    if actions:
        story.append(Paragraph("5. Plano de ação", _PDF_H2))
        action_rows = [["Risco / achado","Ação","Responsável","Prazo","Status"]]
        for a in actions[:20]:
            action_rows.append([
                a.get("risk",""), a.get("action",""), a.get("owner",""),
                a.get("deadline",""), a.get("status",""),
            ])
        story += [_pdf_table(action_rows, [35*mm,64*mm,30*mm,23*mm,22*mm], font_size=6.8), Spacer(1,4*mm)]

    story.append(PageBreak())
    story.append(Paragraph("6. Evidências fotográficas automáticas", _PDF_H2))
    story.append(Paragraph(
        "As evidências são registradas somente em frames válidos de captura. "
        "Quando habilitado, o desfoque facial é aplicado depois da detecção biomecânica e antes do armazenamento da imagem.",
        _PDF_SMALL,
    ))
    story.append(Spacer(1,3*mm))

    if not evidence:
        story.append(Paragraph("Nenhuma evidência foi registrada.", _PDF_BODY))
    else:
        labels = {"TRONCO":"Tronco","PESCOCO":"Pescoço","BRACO":"Braço elevado","JOELHO":"Flexão de joelho"}
        for factor in ["TRONCO","PESCOCO","BRACO","JOELHO"]:
            items = [e for e in evidence if e.get("factor") == factor]
            if not items:
                continue
            story.append(Paragraph(labels[factor], _PDF_H2))
            for e in items[:4]:
                path = Path(e.get("path",""))
                if not path.exists():
                    continue
                try:
                    img = Image(str(path))
                    max_w, max_h = 165*mm, 82*mm
                    ratio = min(max_w/img.imageWidth, max_h/img.imageHeight)
                    img.drawWidth = img.imageWidth * ratio
                    img.drawHeight = img.imageHeight * ratio
                    cap = Paragraph(
                        f"<b>{e.get('date','')} {e.get('clock','')}</b> | "
                        f"t={_fmt_seconds(e.get('elapsed',0))} | "
                        f"valor={_fmt_angle(e.get('value'))} | "
                        f"RULA={e.get('rula','--')} | REBA={e.get('reba','--')} | "
                        f"qualidade={e.get('quality',0):.0f}%",
                        _PDF_SMALL,
                    )
                    story += [KeepTogether([img, Spacer(1,1.2*mm), cap]), Spacer(1,3*mm)]
                except Exception:
                    pass

    story.append(Paragraph("7. Observações e interpretação", _PDF_H2))
    obs = str(metadata.get("observacao","") or "Sem observações adicionais.")
    story.append(Paragraph(obs, _PDF_BODY))
    story.append(Spacer(1,3*mm))
    story.append(Paragraph(
        "<b>Nota técnica:</b> os ângulos são estimados por visão computacional 2D. "
        "RULA e REBA são calculados de forma assistida com parâmetros observacionais confirmados pelo avaliador. "
        "Frames abaixo da qualidade mínima definida são excluídos dos indicadores de exposição.",
        _PDF_SMALL,
    ))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return pdf_path


# ============================================================
# HISTÓRICO V4
# ============================================================
def save_record_v4(snapshot, metadata, rula_result, reba_result, pdf_path):
    row = {
        "avaliacao_id": metadata.get("avaliacao_id",""),
        "data": metadata.get("data",""),
        "inicio": metadata.get("inicio",""),
        "fim": metadata.get("fim",""),
        "setor": metadata.get("setor",""),
        "operacao": metadata.get("operacao",""),
        "colaborador": metadata.get("colaborador",""),
        "turno": metadata.get("turno",""),
        "avaliador": metadata.get("avaliador",""),
        "tempo_s": round(snapshot.get("total_time",0),1),
        "exposicao_pct": round(snapshot.get("risk_pct",0),1),
        "tronco_pct": round(snapshot.get("trunk_pct",0),1),
        "pescoco_pct": round(snapshot.get("neck_pct",0),1),
        "braco_pct": round(snapshot.get("arm_pct",0),1),
        "joelho_pct": round(snapshot.get("knee_pct",0),1),
        "ire_max": snapshot.get("max_ire",0),
        "rula_final": rula_result.get("score","") if rula_result else "",
        "rula_max": snapshot.get("max_rula",0),
        "rula_medio": round(snapshot.get("rula_weighted",0),2),
        "rula_alto_pct": round(snapshot.get("rula_high_pct",0),1),
        "reba_final": reba_result.get("score","") if reba_result else "",
        "reba_max": snapshot.get("max_reba",0),
        "reba_medio": round(snapshot.get("reba_weighted",0),2),
        "reba_alto_pct": round(snapshot.get("reba_high_pct",0),1),
        "qualidade_media_pct": round(snapshot.get("quality_avg",0),1),
        "frames_validos_pct": round(snapshot.get("valid_pct",0),1),
        "ciclos": len(snapshot.get("cycles",[])),
        "evidencias": len(snapshot.get("evidence",[])),
        "pdf": str(pdf_path),
    }
    exists = HISTORY_PATH_V4.exists()
    with HISTORY_PATH_V4.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys(), delimiter=";")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


# ============================================================
# PROCESSADOR DE VÍDEO V4
# ============================================================
class ErgonomiaVideoProcessor:
    FACTOR_LABELS = {
        "TRONCO": "Tronco",
        "PESCOCO": "Pescoço",
        "BRACO": "Braço elevado",
        "JOELHO": "Flexão de joelho",
    }

    def __init__(self, config):
        self.cfg = dict(config)
        self.assessment_id = self.cfg.get("assessment_id","SEMID")
        self.evidence_dir = assessment_evidence_dir(self.assessment_id)
        self.evidence_cooldown = float(self.cfg.get("evidence_cooldown",12))
        self.max_evidence_per_factor = int(self.cfg.get("max_evidence_per_factor",5))
        self.capture_mode = self.cfg.get("capture_mode","Visão normal")
        self.marker_id = int(self.cfg.get("marker_id",0))
        self.min_quality = float(self.cfg.get("min_quality",70))
        self.blur_face = bool(self.cfg.get("blur_face",True))
        self.process_long_side = int(self.cfg.get("process_long_side",960))
        self.requested_width = int(self.cfg.get("requested_width",1280))
        self.requested_height = int(self.cfg.get("requested_height",720))
        self.requested_fps = int(self.cfg.get("requested_fps",30))
        self.camera_label = str(self.cfg.get("camera_label","Traseira"))
        self.rula_opts = dict(self.cfg.get("rula_opts", default_rula_opts()))
        self.reba_opts = dict(self.cfg.get("reba_opts", default_reba_opts()))
        self.lock = threading.RLock()

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=2,
            min_pose_detection_confidence=0.50,
            min_pose_presence_confidence=0.50,
            min_tracking_confidence=0.50,
            output_segmentation_masks=False,
        )
        self.landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

        self.aruco_dict = None
        self.aruco_detector = None
        try:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            if hasattr(cv2.aruco, "ArucoDetector"):
                params = cv2.aruco.DetectorParameters()
                self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, params)
        except Exception:
            pass

        self.last_timestamp_ms = 0
        self.reset(clear_files=False)

    def reset(self, clear_files=False):
        with self.lock:
            if clear_files and self.evidence_dir.exists():
                for p in self.evidence_dir.glob("*.jpg"):
                    try:
                        p.unlink()
                    except Exception:
                        pass

            self.last_tick = time.monotonic()
            self.total_time = 0.0
            self.invalid_time = 0.0
            self.risk_time = 0.0
            self.trunk_time = 0.0
            self.neck_time = 0.0
            self.arm_time = 0.0
            self.knee_time = 0.0
            self.events = 0
            self.current_event_start = None
            self.current_event_duration = 0.0
            self.max_event_duration = 0.0
            self.was_risk = False

            self.max_ire = 0
            self.max_rula = 0
            self.max_reba = 0
            self.worst_pose = None

            self.evidence = []
            self.factor_events = {k:0 for k in self.FACTOR_LABELS}
            self.peak_values = {k:0.0 for k in self.FACTOR_LABELS}
            self.factor_state = {
                k: {"active":False,"last_capture":0.0,"count":0,"peak_captured":0.0}
                for k in self.FACTOR_LABELS
            }

            self.rula_seconds = {i:0.0 for i in range(1,8)}
            self.reba_seconds = {i:0.0 for i in range(1,16)}
            self.time_series = []
            self.last_series_sample = -1.0

            self.quality_integral = 0.0
            self.quality_time = 0.0
            self.quality_min = 100.0
            self.valid_frames = 0
            self.invalid_frames = 0
            self.fps_ema = 0.0

            self.cycle_active = False
            self.cycle_start = None
            self.cycles = []

            self.current = {
                "pose_found":False, "valid_frame":False,
                "trunk":None, "neck":None,
                "shoulder_l":None, "shoulder_r":None,
                "elbow_l":None, "elbow_r":None,
                "wrist_l":None, "wrist_r":None,
                "knee_l":None, "knee_r":None,
                "ire":0, "risk":"SEM LEITURA", "flags":[],
                "rula":0, "reba":0,
                "quality":0.0, "coverage":0.0, "brightness":0.0,
                "blur_score":0.0, "fps":0.0, "resolution":"--",
                "processing_resolution":"--",
                "requested_resolution":f"{self.requested_width}x{self.requested_height}",
                "resolution_ok":False, "orientation":"--",
                "camera_label":self.camera_label,
                "marker_found":False, "marker_count":0,
            }

    def start_cycle(self):
        with self.lock:
            if self.cycle_active:
                return False, "Já existe um ciclo em andamento."
            self.cycle_active = True
            self.cycle_start = {
                "time": self.total_time,
                "risk": self.risk_time,
                "trunk": self.trunk_time,
                "neck": self.neck_time,
                "arm": self.arm_time,
                "knee": self.knee_time,
                "series_index": len(self.time_series),
            }
            return True, f"Ciclo {len(self.cycles)+1} iniciado."

    def finish_cycle(self):
        with self.lock:
            if not self.cycle_active or not self.cycle_start:
                return False, "Nenhum ciclo em andamento."

            s = self.cycle_start
            duration = max(0.0, self.total_time - s["time"])
            segment = self.time_series[s["series_index"]:]
            if duration <= 0:
                self.cycle_active = False
                self.cycle_start = None
                return False, "O ciclo ainda não possui tempo válido."

            rulas = [x["rula"] for x in segment if x.get("rula")]
            rebas = [x["reba"] for x in segment if x.get("reba")]

            cycle = {
                "cycle": len(self.cycles)+1,
                "duration": duration,
                "risk_pct": 100*(self.risk_time-s["risk"])/duration,
                "trunk_pct": 100*(self.trunk_time-s["trunk"])/duration,
                "neck_pct": 100*(self.neck_time-s["neck"])/duration,
                "arm_pct": 100*(self.arm_time-s["arm"])/duration,
                "knee_pct": 100*(self.knee_time-s["knee"])/duration,
                "max_rula": max(rulas) if rulas else 0,
                "max_reba": max(rebas) if rebas else 0,
                "mean_rula": float(np.mean(rulas)) if rulas else 0.0,
                "mean_reba": float(np.mean(rebas)) if rebas else 0.0,
            }
            self.cycles.append(cycle)
            self.cycle_active = False
            self.cycle_start = None
            return True, f"Ciclo {cycle['cycle']} finalizado."

    def _marker_detection(self, gray):
        corners, ids = [], None
        if self.aruco_dict is None:
            return corners, ids
        try:
            if self.aruco_detector is not None:
                corners, ids, _ = self.aruco_detector.detectMarkers(gray)
            else:
                corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict)
        except Exception:
            corners, ids = [], None
        return corners, ids

    def _select_pose(self, poses, marker_center_norm=None):
        if not poses:
            return None

        def pose_quality(lm):
            vals = []
            for idx in QUALITY_LANDMARKS:
                obj = lm[idx]
                vals.append(float(getattr(obj,"visibility",1.0) or 0))
            return float(np.mean(vals)) if vals else 0.0

        if marker_center_norm is not None:
            best = None
            best_dist = float("inf")
            for lm in poses:
                try:
                    torso = (
                        midpoint(lm,L_SHOULDER,R_SHOULDER) +
                        midpoint(lm,L_HIP,R_HIP)
                    ) / 2.0
                    dist = float(np.linalg.norm(torso - marker_center_norm))
                    if dist < best_dist:
                        best, best_dist = lm, dist
                except Exception:
                    pass
            if best is not None:
                return best

        return max(poses, key=pose_quality)

    def _capture_quality(self, image, lm, marker_found):
        h,w = image.shape[:2]

        # Nitidez/iluminação não precisam ser calculadas em Full HD.
        # Isso reduz CPU sem alterar a resolução das evidências.
        sample = image
        long_side = max(h,w)
        if long_side > 960:
            scale = 960.0 / float(long_side)
            sw = max(2, int(round(w*scale)))
            sh = max(2, int(round(h*scale)))
            sample = cv2.resize(image,(sw,sh),interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        blur_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        visible_count = 0
        for idx in QUALITY_LANDMARKS:
            obj = lm[idx]
            vis = float(getattr(obj,"visibility",1.0) or 0.0)
            pres = float(getattr(obj,"presence",1.0) or 0.0)
            if vis >= 0.45 and pres >= 0.45:
                visible_count += 1
        coverage = 100.0 * visible_count / len(QUALITY_LANDMARKS)

        brightness_score = clamp(100.0 - abs(brightness - 130.0) * 0.95, 0, 100)
        blur_score = clamp(blur_var / 160.0 * 100.0, 0, 100)

        req_w,req_h = self.requested_width,self.requested_height
        direct_ok = w >= int(req_w*0.80) and h >= int(req_h*0.80)
        swapped_ok = h >= int(req_w*0.80) and w >= int(req_h*0.80)
        resolution_ok = bool(direct_ok or swapped_ok)

        if resolution_ok:
            resolution_score = 100.0
        elif w >= 640 and h >= 360:
            resolution_score = 78.0
        else:
            resolution_score = 50.0

        marker_score = 100.0 if self.capture_mode == "Visão normal" or marker_found else 0.0

        quality = (
            0.55*coverage +
            0.15*brightness_score +
            0.10*blur_score +
            0.10*resolution_score +
            0.10*marker_score
        )
        return {
            "quality":float(clamp(quality,0,100)),
            "coverage":coverage,
            "brightness":brightness,
            "blur_score":blur_score,
            "resolution":f"{w}x{h}",
            "resolution_ok":resolution_ok,
        }

    def _blur_face_region(self, image, lm):
        if not self.blur_face:
            return
        h,w = image.shape[:2]
        pts = []
        for idx in [0,L_EAR,R_EAR]:
            try:
                x=int(lm[idx].x*w); y=int(lm[idx].y*h)
                pts.append((x,y))
            except Exception:
                pass
        if not pts:
            return
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        cx=int(np.mean(xs)); cy=int(np.mean(ys))
        size=max(45, int(abs(max(xs)-min(xs))*1.8 + 45))
        x1=clamp(cx-size,0,w-1); x2=clamp(cx+size,0,w)
        y1=clamp(cy-size,0,h-1); y2=clamp(cy+size,0,h)
        x1,x2,y1,y2=map(int,[x1,x2,y1,y2])
        if x2>x1 and y2>y1:
            roi=image[y1:y2,x1:x2]
            if roi.size:
                k=max(21, (min(roi.shape[:2])//4)*2+1)
                k=min(k,99)
                if k % 2 == 0: k += 1
                image[y1:y2,x1:x2]=cv2.GaussianBlur(roi,(k,k),0)

    def _draw_skeleton(self, image, lm):
        h,w=image.shape[:2]
        for a,b in POSE_CONNECTIONS:
            if visible(lm,a) and visible(lm,b):
                p1=(int(lm[a].x*w),int(lm[a].y*h))
                p2=(int(lm[b].x*w),int(lm[b].y*h))
                cv2.line(image,p1,p2,(60,222,255),3,cv2.LINE_AA)
        for idx in QUALITY_LANDMARKS:
            if visible(lm,idx):
                p=(int(lm[idx].x*w),int(lm[idx].y*h))
                cv2.circle(image,p,6,(255,255,255),-1,cv2.LINE_AA)
                cv2.circle(image,p,8,(60,222,255),2,cv2.LINE_AA)

    def _draw_markers(self, image, corners, ids):
        if ids is None or len(corners) == 0:
            return
        try:
            cv2.aruco.drawDetectedMarkers(image,corners,ids)
        except Exception:
            pass

    def _overlay(self, image, values):
        h,w=image.shape[:2]
        overlay=image.copy()
        cv2.rectangle(overlay,(12,12),(min(610,w-12),318),(8,18,31),-1)
        cv2.addWeighted(overlay,.84,image,.16,0,image)

        if values.get("valid_frame"):
            status_color=(90,230,150)
            status="FRAME VALIDO"
        else:
            status_color=(70,70,255)
            status="MEDICAO PAUSADA"

        cv2.putText(image,status,(28,42),cv2.FONT_HERSHEY_SIMPLEX,.65,status_color,2,cv2.LINE_AA)
        cv2.putText(
            image,
            f"Qualidade {values.get('quality',0):.0f}% | FPS {values.get('fps',0):.1f} | Cobertura {values.get('coverage',0):.0f}%",
            (28,68),cv2.FONT_HERSHEY_SIMPLEX,.48,(225,238,250),1,cv2.LINE_AA
        )
        cv2.putText(
            image,
            f"Captura {values.get('resolution','--')} | IA {values.get('processing_resolution','--')} | {self.camera_label}",
            (28,90),cv2.FONT_HERSHEY_SIMPLEX,.40,(175,210,235),1,cv2.LINE_AA
        )
        cv2.putText(
            image,
            f"IRE {values.get('ire',0)} | RULA {values.get('rula',0)}/7 | REBA {values.get('reba',0)}/15",
            (28,118),cv2.FONT_HERSHEY_SIMPLEX,.62,(100,230,255),2,cv2.LINE_AA
        )

        lines=[
            f"Tronco: {fmt_angle(values.get('trunk'))}",
            f"Pescoco*: {fmt_angle(values.get('neck'))}",
            f"Braco E/D: {fmt_angle(values.get('shoulder_l'))} / {fmt_angle(values.get('shoulder_r'))}",
            f"Cotovelo E/D: {fmt_angle(values.get('elbow_l'))} / {fmt_angle(values.get('elbow_r'))}",
            f"Punho E/D*: {fmt_angle(values.get('wrist_l'))} / {fmt_angle(values.get('wrist_r'))}",
            f"Joelho E/D: {fmt_angle(values.get('knee_l'))} / {fmt_angle(values.get('knee_r'))}",
        ]
        y=148
        for line in lines:
            cv2.putText(image,line,(28,y),cv2.FONT_HERSHEY_SIMPLEX,.46,(238,244,250),1,cv2.LINE_AA)
            y += 22

        marker_txt = (
            f"ArUco ID {self.marker_id}: {'OK' if values.get('marker_found') else 'NAO ENCONTRADO'}"
            if self.capture_mode != "Visão normal"
            else "Modo: visao sem marcador"
        )
        cv2.putText(image,marker_txt,(28,286),cv2.FONT_HERSHEY_SIMPLEX,.42,(190,215,235),1,cv2.LINE_AA)
        if values.get("flags"):
            cv2.putText(image," | ".join(values["flags"]),(28,307),cv2.FONT_HERSHEY_SIMPLEX,.39,(80,205,255),1,cv2.LINE_AA)

    def _capture_evidence(self, image, factor, value, values, now):
        state=self.factor_state[factor]
        if state["count"] >= self.max_evidence_per_factor:
            return
        dt_clock=datetime.now()
        stamp=dt_clock.strftime("%Y%m%d_%H%M%S_%f")[:-3]
        path=self.evidence_dir/f"{factor.lower()}_{stamp}.jpg"

        shot=image.copy()
        h,w=shot.shape[:2]
        cv2.rectangle(shot,(12,max(12,h-94)),(min(w-12,790),h-12),(8,18,31),-1)
        cv2.putText(
            shot,
            f"{self.FACTOR_LABELS[factor]} | {value:.1f} deg | RULA {values.get('rula',0)} | REBA {values.get('reba',0)}",
            (24,h-62),cv2.FONT_HERSHEY_SIMPLEX,.54,(255,255,255),2,cv2.LINE_AA
        )
        cv2.putText(
            shot,
            f"Avaliacao {self.assessment_id} | {dt_clock.strftime('%d/%m/%Y %H:%M:%S')} | t={fmt_seconds(self.total_time)} | qualidade {values.get('quality',0):.0f}%",
            (24,h-31),cv2.FONT_HERSHEY_SIMPLEX,.43,(210,225,240),1,cv2.LINE_AA
        )
        if cv2.imwrite(str(path),shot,[int(cv2.IMWRITE_JPEG_QUALITY),90]):
            self.evidence.append({
                "factor":factor,"path":str(path),
                "clock":dt_clock.strftime("%H:%M:%S"),
                "date":dt_clock.strftime("%d/%m/%Y"),
                "elapsed":self.total_time,
                "value":float(value),"risk":values.get("risk",""),
                "ire":int(values.get("ire",0)),
                "rula":int(values.get("rula",0)),
                "reba":int(values.get("reba",0)),
                "quality":float(values.get("quality",0)),
            })
            state["count"] += 1
            state["last_capture"] = now
            state["peak_captured"] = max(state["peak_captured"],float(value))

    def _process_evidence(self, image, active_map, values, now):
        severity={
            "TRONCO":float(values.get("trunk") or 0),
            "PESCOCO":float(values.get("neck") or 0),
            "BRACO":max([v for v in [values.get("shoulder_l"),values.get("shoulder_r")] if v is not None] or [0]),
            "JOELHO":max(0.0,180.0-min([v for v in [values.get("knee_l"),values.get("knee_r")] if v is not None] or [180])),
        }
        for factor,is_active in active_map.items():
            state=self.factor_state[factor]
            val=severity[factor]
            if val > self.peak_values[factor]:
                self.peak_values[factor]=val
            just_started=is_active and not state["active"]
            if just_started:
                self.factor_events[factor] += 1

            capture=False
            if just_started and (state["count"]==0 or now-state["last_capture"]>=self.evidence_cooldown):
                capture=True
            elif is_active and val > state["peak_captured"] + 5 and now-state["last_capture"]>=self.evidence_cooldown:
                capture=True

            if capture:
                self._capture_evidence(image,factor,val,values,now)
            state["active"]=bool(is_active)

    def snapshot(self):
        with self.lock:
            valid_total = self.total_time + self.invalid_time
            score_total = sum(self.rula_seconds.values())
            out=dict(self.current)
            out.update({
                "total_time":self.total_time,
                "invalid_time":self.invalid_time,
                "risk_pct":100*self.risk_time/self.total_time if self.total_time else 0,
                "trunk_pct":100*self.trunk_time/self.total_time if self.total_time else 0,
                "neck_pct":100*self.neck_time/self.total_time if self.total_time else 0,
                "arm_pct":100*self.arm_time/self.total_time if self.total_time else 0,
                "knee_pct":100*self.knee_time/self.total_time if self.total_time else 0,
                "valid_pct":100*self.total_time/valid_total if valid_total else 0,
                "events":self.events,
                "current_event_duration":self.current_event_duration,
                "max_event_duration":self.max_event_duration,
                "max_ire":self.max_ire,
                "max_rula":self.max_rula,
                "max_reba":self.max_reba,
                "worst_pose":dict(self.worst_pose) if self.worst_pose else None,
                "evidence":[dict(x) for x in self.evidence],
                "factor_events":dict(self.factor_events),
                "peak_values":dict(self.peak_values),
                "rula_seconds":dict(self.rula_seconds),
                "reba_seconds":dict(self.reba_seconds),
                "rula_dominant":_dominant_score(self.rula_seconds),
                "reba_dominant":_dominant_score(self.reba_seconds),
                "rula_weighted":_weighted_score(self.rula_seconds),
                "reba_weighted":_weighted_score(self.reba_seconds),
                "rula_high_pct":100*sum(v for k,v in self.rula_seconds.items() if k>=5)/score_total if score_total else 0,
                "reba_high_pct":100*sum(v for k,v in self.reba_seconds.items() if k>=8)/sum(self.reba_seconds.values()) if sum(self.reba_seconds.values()) else 0,
                "time_series":[dict(x) for x in self.time_series],
                "cycles":[dict(x) for x in self.cycles],
                "cycle_active":self.cycle_active,
                "quality_avg":self.quality_integral/self.quality_time if self.quality_time else 0,
                "quality_min":self.quality_min if self.quality_time else 0,
            })
            return out

    def recv(self, frame):
        image=frame.to_ndarray(format="bgr24")
        original_h,original_w=image.shape[:2]

        now=time.monotonic()
        raw_dt=now-self.last_tick
        dt=clamp(raw_dt,0.0,0.25)
        self.last_tick=now
        inst_fps=1.0/raw_dt if raw_dt>1e-4 else 0
        self.fps_ema=inst_fps if self.fps_ema<=0 else 0.90*self.fps_ema+0.10*inst_fps

        ts=int(now*1000)
        if ts<=self.last_timestamp_ms:
            ts=self.last_timestamp_ms+1
        self.last_timestamp_ms=ts

        # ArUco só é procurado quando o modo de marcador está realmente em uso.
        corners,ids=[],None
        marker_found=False
        marker_center_norm=None
        marker_count=0
        if self.capture_mode != "Visão normal":
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            corners,ids=self._marker_detection(gray)
            if ids is not None:
                flat_ids=[int(x) for x in np.asarray(ids).flatten().tolist()]
                marker_count=len(flat_ids)
                if self.marker_id in flat_ids:
                    marker_found=True
                    idx=flat_ids.index(self.marker_id)
                    c=np.asarray(corners[idx]).reshape(-1,2)
                    cx,cy=np.mean(c,axis=0)
                    marker_center_norm=np.array([cx/original_w,cy/original_h],dtype=np.float32)

        # O frame que volta ao tablet e as evidências permanecem na resolução original.
        # Somente a imagem enviada ao MediaPipe é reduzida.
        process_image=image
        long_side=max(original_h,original_w)
        if long_side > self.process_long_side:
            scale=self.process_long_side/float(long_side)
            process_w=max(2,int(round(original_w*scale)))
            process_h=max(2,int(round(original_h*scale)))
            process_image=cv2.resize(image,(process_w,process_h),interpolation=cv2.INTER_AREA)
        else:
            process_h,process_w=original_h,original_w

        rgb=cv2.cvtColor(process_image,cv2.COLOR_BGR2RGB)
        mp_image=mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb)
        try:
            result=self.landmarker.detect_for_video(mp_image,ts)
        except Exception:
            result=None

        req_w,req_h=self.requested_width,self.requested_height
        direct_ok=original_w>=int(req_w*0.80) and original_h>=int(req_h*0.80)
        swapped_ok=original_h>=int(req_w*0.80) and original_w>=int(req_h*0.80)
        resolution_ok=bool(direct_ok or swapped_ok)
        orientation="Paisagem" if original_w>=original_h else "Retrato"
        requested_resolution=f"{req_w}x{req_h}"
        processing_resolution=f"{process_w}x{process_h}"

        poses=result.pose_landmarks if result and result.pose_landmarks else []
        lm=self._select_pose(poses,marker_center_norm if marker_found else None)

        if lm is None:
            with self.lock:
                self.invalid_time += dt
                self.invalid_frames += 1
                self.current.update({
                    "pose_found":False,"valid_frame":False,"quality":0.0,
                    "risk":"SEM LEITURA","flags":[],"fps":self.fps_ema,
                    "marker_found":marker_found,"marker_count":marker_count,
                    "resolution":f"{original_w}x{original_h}",
                    "processing_resolution":processing_resolution,
                    "requested_resolution":requested_resolution,
                    "resolution_ok":resolution_ok,
                    "orientation":orientation,
                    "camera_label":self.camera_label,
                })
            self._draw_markers(image,corners,ids)
            cv2.rectangle(image,(15,15),(min(650,original_w-15),82),(20,20,20),-1)
            cv2.putText(image,"Corpo nao detectado - medicao pausada",(28,53),
                        cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),2,cv2.LINE_AA)
            cv2.putText(image,f"Captura {original_w}x{original_h} | IA {processing_resolution}",
                        (28,74),cv2.FONT_HERSHEY_SIMPLEX,.40,(190,215,235),1,cv2.LINE_AA)
            return av.VideoFrame.from_ndarray(image,format="bgr24")

        quality=self._capture_quality(image,lm,marker_found)
        marker_required = self.capture_mode != "Visão normal"
        valid_frame = quality["quality"] >= self.min_quality and (marker_found or not marker_required)

        self._draw_markers(image,corners,ids)
        self._draw_skeleton(image,lm)

        def can(*idxs):
            return all(visible(lm,i) for i in idxs)

        tr=trunk_angle(lm) if can(L_SHOULDER,R_SHOULDER,L_HIP,R_HIP) else None
        ne=neck_angle(lm) if can(L_EAR,R_EAR,L_SHOULDER,R_SHOULDER,L_HIP,R_HIP) else None
        sh_l=shoulder_angle(lm,L_HIP,L_SHOULDER,L_ELBOW) if can(L_HIP,L_SHOULDER,L_ELBOW) else None
        sh_r=shoulder_angle(lm,R_HIP,R_SHOULDER,R_ELBOW) if can(R_HIP,R_SHOULDER,R_ELBOW) else None
        el_l=elbow_angle(lm,L_SHOULDER,L_ELBOW,L_WRIST) if can(L_SHOULDER,L_ELBOW,L_WRIST) else None
        el_r=elbow_angle(lm,R_SHOULDER,R_ELBOW,R_WRIST) if can(R_SHOULDER,R_ELBOW,R_WRIST) else None
        wr_l=wrist_deviation_angle(lm,L_ELBOW,L_WRIST,L_INDEX,L_PINKY) if can(L_ELBOW,L_WRIST,L_INDEX,L_PINKY) else None
        wr_r=wrist_deviation_angle(lm,R_ELBOW,R_WRIST,R_INDEX,R_PINKY) if can(R_ELBOW,R_WRIST,R_INDEX,R_PINKY) else None
        kn_l=knee_angle(lm,L_HIP,L_KNEE,L_ANKLE) if can(L_HIP,L_KNEE,L_ANKLE) else None
        kn_r=knee_angle(lm,R_HIP,R_KNEE,R_ANKLE) if can(R_HIP,R_KNEE,R_ANKLE) else None

        trunk_flag=tr is not None and tr>=self.cfg["trunk_limit"]
        neck_flag=ne is not None and ne>=self.cfg["neck_limit"]
        arm_vals=[v for v in [sh_l,sh_r] if v is not None]
        knee_vals=[v for v in [kn_l,kn_r] if v is not None]
        arm_flag=bool(arm_vals) and max(arm_vals)>=self.cfg["arm_limit"]
        knee_flag=bool(knee_vals) and min(knee_vals)<=self.cfg["knee_limit"]

        flags=[]
        if trunk_flag: flags.append("TRONCO")
        if neck_flag: flags.append("PESCOÇO")
        if arm_flag: flags.append("BRAÇO ELEVADO")
        if knee_flag: flags.append("FLEXÃO JOELHO")

        values={
            "pose_found":True,"valid_frame":valid_frame,
            "trunk":tr,"neck":ne,
            "shoulder_l":sh_l,"shoulder_r":sh_r,
            "elbow_l":el_l,"elbow_r":el_r,
            "wrist_l":wr_l,"wrist_r":wr_r,
            "knee_l":kn_l,"knee_r":kn_r,
            "flags":flags if valid_frame else [],
            "quality":quality["quality"],"coverage":quality["coverage"],
            "brightness":quality["brightness"],"blur_score":quality["blur_score"],
            "resolution":quality["resolution"],"fps":self.fps_ema,
            "processing_resolution":processing_resolution,
            "requested_resolution":requested_resolution,
            "resolution_ok":quality.get("resolution_ok",resolution_ok),
            "orientation":orientation,
            "camera_label":self.camera_label,
            "marker_found":marker_found,"marker_count":marker_count,
        }
        values["ire"]=calc_ire(values,self.cfg) if valid_frame else 0
        values["risk"]=risk_label(len(flags)) if valid_frame else "PAUSADO"

        try:
            rr=calculate_rula(values,self.rula_opts) if valid_frame else {"score":0}
            rb=calculate_reba(values,self.reba_opts) if valid_frame else {"score":0}
            values["rula"]=int(rr.get("score",0))
            values["reba"]=int(rb.get("score",0))
        except Exception:
            values["rula"]=0
            values["reba"]=0

        # Privacidade: detectar primeiro, desfocar depois.
        self._blur_face_region(image,lm)
        self._overlay(image,values)

        with self.lock:
            self.current=values
            if not valid_frame:
                self.invalid_time += dt
                self.invalid_frames += 1
                return av.VideoFrame.from_ndarray(image,format="bgr24")

            self.valid_frames += 1
            self.total_time += dt
            self.quality_integral += values["quality"]*dt
            self.quality_time += dt
            self.quality_min=min(self.quality_min,values["quality"])

            if trunk_flag: self.trunk_time += dt
            if neck_flag: self.neck_time += dt
            if arm_flag: self.arm_time += dt
            if knee_flag: self.knee_time += dt

            risk_now=bool(flags)
            if risk_now:
                self.risk_time += dt
                if not self.was_risk:
                    self.events += 1
                    self.current_event_start=now
                self.current_event_duration=now-self.current_event_start if self.current_event_start else 0
                self.max_event_duration=max(self.max_event_duration,self.current_event_duration)
            else:
                self.current_event_start=None
                self.current_event_duration=0.0
            self.was_risk=risk_now

            self.max_ire=max(self.max_ire,values["ire"])
            self.max_rula=max(self.max_rula,values["rula"])
            self.max_reba=max(self.max_reba,values["reba"])
            if self.worst_pose is None or values["ire"] >= self.worst_pose.get("ire",-1):
                self.worst_pose=dict(values)

            if values["rula"] in self.rula_seconds:
                self.rula_seconds[values["rula"]] += dt
            if values["reba"] in self.reba_seconds:
                self.reba_seconds[values["reba"]] += dt

            if self.total_time-self.last_series_sample >= 0.5:
                self.time_series.append({
                    "tempo_s":round(self.total_time,1),
                    "tronco":tr,"pescoco":ne,
                    "braco_d":sh_r,"braco_e":sh_l,
                    "joelho_d":kn_r,"joelho_e":kn_l,
                    "ire":values["ire"],"rula":values["rula"],"reba":values["reba"],
                    "qualidade":values["quality"],
                })
                self.last_series_sample=self.total_time
                if len(self.time_series)>7200:
                    self.time_series=self.time_series[-7200:]

            active_map={"TRONCO":trunk_flag,"PESCOCO":neck_flag,"BRACO":arm_flag,"JOELHO":knee_flag}
            # A evidência é salva do frame original recebido, não da cópia reduzida da IA.
            self._process_evidence(image,active_map,values,now)

        return av.VideoFrame.from_ndarray(image,format="bgr24")

    def __del__(self):
        try:
            self.landmarker.close()
        except Exception:
            pass


# ============================================================
# INTERFACE MVP 04
# ============================================================
st.set_page_config(
    page_title=APP_TITLE, page_icon="🧍", layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
:root{
 --bg:#06111d;--panel:#0d1e31;--line:rgba(119,190,237,.18);
 --muted:#8fa7bf;--text:#eff6ff;--cyan:#58dcff
}
.stApp{
 background:
 radial-gradient(circle at 8% 0%,rgba(31,116,180,.22),transparent 30%),
 radial-gradient(circle at 92% 4%,rgba(23,178,190,.09),transparent 24%),
 linear-gradient(180deg,#06101c 0%,#091522 100%);
 color:var(--text)
}
section[data-testid="stSidebar"]{
 background:linear-gradient(180deg,#07111f 0%,#091827 100%);
 border-right:1px solid var(--line)
}
.block-container{padding-top:1.15rem;max-width:1580px}
div[data-testid="stMetric"]{
 background:linear-gradient(145deg,rgba(16,35,58,.96),rgba(8,23,40,.96));
 border:1px solid var(--line);padding:12px 14px;border-radius:15px
}
div[data-testid="stMetricLabel"]{color:#8fa7bf}
div[data-testid="stMetricValue"]{font-weight:850}
.brand{display:flex;align-items:center;gap:13px;margin-bottom:4px}
.logo{width:50px;height:50px;border-radius:15px;display:flex;align-items:center;justify-content:center;
 background:rgba(54,190,235,.12);border:1px solid rgba(87,214,255,.28);font-size:24px}
.title{font-size:2rem;font-weight:880;letter-spacing:-.025em;line-height:1}
.subtitle{color:var(--muted);margin-top:7px;margin-bottom:16px}
.info-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px;margin:12px 0 18px}
.info{background:linear-gradient(145deg,rgba(16,35,58,.89),rgba(8,23,40,.90));
 border:1px solid var(--line);border-radius:14px;padding:11px 13px;min-height:72px}
.lbl{font-size:.67rem;color:#839ab2;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.val{font-size:.94rem;font-weight:800;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.panel{background:linear-gradient(145deg,rgba(14,31,51,.86),rgba(8,22,38,.88));
 border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin-bottom:12px}
.panel-title{font-size:1rem;font-weight:850}.panel-sub{color:var(--muted);font-size:.82rem;margin-top:4px}
.score-box{background:linear-gradient(145deg,rgba(15,35,58,.95),rgba(9,24,42,.96));
 border:1px solid var(--line);border-radius:18px;padding:14px;text-align:center}
.score-number{font-size:2.55rem;font-weight:900;line-height:1}
.score-caption{color:#94a9be;font-size:.73rem;margin-top:7px}
.tag{display:inline-block;padding:5px 9px;border-radius:999px;margin-top:8px;font-size:.73rem;font-weight:850;
 border:1px solid rgba(88,220,255,.25);background:rgba(88,220,255,.08);color:#8ce8ff}
.quality-card{border-radius:16px;padding:15px;border:1px solid rgba(115,190,230,.18);
 background:linear-gradient(145deg,rgba(16,35,58,.94),rgba(8,23,40,.96))}
.heatgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.heat{border:1px solid rgba(120,180,220,.14);border-radius:13px;padding:12px;background:rgba(20,40,60,.55)}
.heatname{font-weight:800}.heatpct{font-size:1.45rem;font-weight:900;margin-top:4px}
.small-muted{font-size:.77rem;color:#91a9bf}
.camera-spec{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0 0 10px}
.camera-spec>div{border:1px solid rgba(115,190,230,.16);border-radius:12px;padding:9px 11px;background:rgba(12,28,46,.72)}
.camera-spec .c-label{font-size:.62rem;color:#819ab2;font-weight:800;text-transform:uppercase;letter-spacing:.06em}
.camera-spec .c-value{font-size:.88rem;color:#eff6ff;font-weight:850;margin-top:4px}

/* O vídeo WebRTC deve usar toda a largura disponível, sem crop. */
video{
 width:100%!important;
 height:auto!important;
 max-height:72vh!important;
 object-fit:contain!important;
 background:#020812!important;
 border-radius:15px!important;
}

@media(max-width:1100px){
 .block-container{padding-top:.7rem;padding-left:.75rem;padding-right:.75rem}
 .title{font-size:1.45rem}
 .subtitle{font-size:.84rem;margin-bottom:10px}
 .info-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
 .info{min-height:62px;padding:9px 10px}
 .panel{padding:11px 12px}
 .camera-spec{grid-template-columns:repeat(3,minmax(0,1fr))}
 video{max-height:62vh!important}
}
@media(max-width:650px){
 .camera-spec{grid-template-columns:1fr}
 .info-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
 .title{font-size:1.25rem}
 .logo{width:42px;height:42px}
 video{max-height:58vh!important}
}
</style>
""", unsafe_allow_html=True)

# Estado adicional
for k,v in {
    "actions":[],
    "final_pdf":None,
    "captured_pose":None,
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧍 Ergonomia por Visão")
    st.caption(f"Avaliação **{st.session_state.assessment_id}**")

    st.markdown("### Identificação")
    st.session_state.setor=st.text_input("Setor *",value=st.session_state.setor,placeholder="Ex.: Estamparia")
    st.session_state.operacao=st.text_input("Operação / Posto *",value=st.session_state.operacao,placeholder="Ex.: Prensa 11 - Abastecimento")
    st.session_state.colaborador=st.text_input("Colaborador *",value=st.session_state.colaborador,placeholder="Nome / matrícula")
    turns=["1º Turno","2º Turno","Administrativo","Outro"]
    st.session_state.turno=st.selectbox("Turno",turns,index=turns.index(st.session_state.turno) if st.session_state.turno in turns else 0)
    st.session_state.avaliador=st.text_input("Avaliador",value=st.session_state.avaliador)
    st.session_state.observacao=st.text_area("Observação",value=st.session_state.observacao,height=65)

    st.markdown("### Captura")
    capture_mode=st.radio("Modo",["Visão normal","Visão + marcador ArUco"],index=0)
    marker_id=st.number_input("ID ArUco do colaborador",min_value=0,max_value=49,value=0,step=1,disabled=capture_mode=="Visão normal")

    camera_facing=st.selectbox(
        "Câmera preferida",
        ["Traseira principal","Frontal"],
        index=0,
        help="No tablet, a traseira principal é a opção recomendada. Evite ultrawide para medição angular."
    )
    camera_profile_name=st.selectbox(
        "Qualidade da câmera",
        list(CAMERA_PROFILES.keys()),
        index=0,
        help="Industrial 720p é o padrão recomendado. 1080p usa 24 FPS para reduzir compressão e carga."
    )
    camera_profile=CAMERA_PROFILES[camera_profile_name]
    layout_mode=st.radio("Layout",["Tablet / celular","Desktop"],index=0,horizontal=True)

    min_quality=st.slider("Qualidade mínima para contabilizar frame",40,95,70,1,format="%d%%")
    blur_face=st.checkbox("Desfocar rosto nas evidências",value=True)
    st.caption(
        "Use o tablet em paisagem. A captura fica em alta resolução; "
        "a IA analisa uma cópia menor para manter fluidez."
    )
    if capture_mode!="Visão normal":
        st.caption("No modo ArUco, frames sem o marcador alvo são descartados.")

    st.markdown("### Limiares do IRE")
    trunk_limit=st.slider("Tronco",10,60,25,1,format="%d°")
    neck_limit=st.slider("Pescoço",10,60,25,1,format="%d°")
    arm_limit=st.slider("Braço",30,120,60,5,format="%d°")
    knee_limit=st.slider("Joelho",90,170,130,5,format="%d°")

    st.markdown("### Evidências")
    evidence_cooldown=st.slider("Intervalo mínimo entre fotos",5,60,12,1,format="%d s")
    max_evidence_per_factor=st.slider("Máximo de fotos por fator",1,10,5)

with st.sidebar.expander("RULA / REBA - fatores observacionais",expanded=False):
    st.caption("Os ângulos vêm da visão. Confirme fatores que a câmera 2D não determina com segurança.")
    side_live=st.radio("Lado principal",["Direito","Esquerdo"],horizontal=True)
    shoulder_raised=st.checkbox("Ombro elevado")
    abducted=st.checkbox("Braço abduzido")
    arm_supported=st.checkbox("Braço apoiado")
    across=st.checkbox("Antebraço cruza linha média")
    wrist_midline=st.checkbox("Punho desviado da linha média")
    wrist_twist=st.checkbox("Punho torcido/desviado")
    neck_extension=st.checkbox("Pescoço em extensão")
    neck_twisted=st.checkbox("Pescoço rotacionado")
    neck_side=st.checkbox("Pescoço inclinado lateralmente")
    trunk_twisted=st.checkbox("Tronco rotacionado")
    trunk_side=st.checkbox("Tronco inclinado lateralmente")
    legs_supported=st.checkbox("Pernas/pés apoiados",value=True)
    seated=st.checkbox("Trabalho sentado")
    muscle_use=st.selectbox("RULA - uso muscular",[0,1],format_func=lambda x:"0 - não" if x==0 else "1 - estático/repetitivo")
    rula_force=st.selectbox("RULA - força/carga",[0,1,2,3])
    reba_load=st.selectbox("REBA - carga",[0,1,2],format_func=lambda x:{0:"0 - <5 kg",1:"1 - 5 a 10 kg",2:"2 - >10 kg"}[x])
    shock_force=st.checkbox("REBA - força súbita/choque")
    coupling=st.selectbox("REBA - pega/acoplamento",[0,1,2,3],format_func=lambda x:{0:"0 - boa",1:"1 - aceitável",2:"2 - ruim",3:"3 - inaceitável"}[x])
    static_posture=st.checkbox("REBA - postura estática >1 min")
    repetition=st.checkbox("REBA - repetição >4/min")
    rapid_changes=st.checkbox("REBA - mudanças rápidas/base instável")

rula_opts_live={
    "side":side_live,"shoulder_raised":shoulder_raised,"abducted":abducted,
    "arm_supported":arm_supported,"across":across,"wrist_midline":wrist_midline,
    "wrist_twist_extreme":wrist_twist,"neck_extension":neck_extension,
    "neck_twisted":neck_twisted,"neck_side":neck_side,
    "trunk_twisted":trunk_twisted,"trunk_side":trunk_side,
    "legs_supported":legs_supported,"muscle_use":muscle_use,"force_score":rula_force,
}
reba_opts_live={
    "side":side_live,"shoulder_raised":shoulder_raised,"abducted":abducted,
    "arm_supported":arm_supported,"neck_extension":neck_extension,
    "neck_twisted":neck_twisted,"neck_side":neck_side,
    "trunk_twisted":trunk_twisted,"trunk_side":trunk_side,
    "legs_supported":legs_supported,"seated":seated,"wrist_twisted":wrist_twist,
    "load_score":reba_load,"shock_force":shock_force,"coupling_score":coupling,
    "static_posture":static_posture,"repetition":repetition,"rapid_changes":rapid_changes,
}

cfg={
    "trunk_limit":float(trunk_limit),"neck_limit":float(neck_limit),
    "arm_limit":float(arm_limit),"knee_limit":float(knee_limit),
    "assessment_id":st.session_state.assessment_id,
    "evidence_cooldown":evidence_cooldown,
    "max_evidence_per_factor":max_evidence_per_factor,
    "capture_mode":capture_mode,"marker_id":int(marker_id),
    "min_quality":float(min_quality),"blur_face":blur_face,
    "rula_opts":rula_opts_live,"reba_opts":reba_opts_live,
    "process_long_side":int(camera_profile["process_long_side"]),
    "requested_width":int(camera_profile["width"]),
    "requested_height":int(camera_profile["height"]),
    "requested_fps":int(camera_profile["fps"]),
    "camera_label":camera_facing,
}

camera_facing_mode="environment" if camera_facing=="Traseira principal" else "user"
camera_constraints={
    "video":{
        "facingMode":{"ideal":camera_facing_mode},
        "width":{
            "min":640,
            "ideal":int(camera_profile["width"]),
            "max":int(camera_profile["width"]),
        },
        "height":{
            "min":360,
            "ideal":int(camera_profile["height"]),
            "max":int(camera_profile["height"]),
        },
        "aspectRatio":{"ideal":16/9},
        "frameRate":{
            "min":20,
            "ideal":int(camera_profile["fps"]),
            "max":int(camera_profile["fps"]),
        },
    },
    "audio":False,
}

ok,err=ensure_model()
if not ok:
    st.error(f"Não foi possível carregar o modelo MediaPipe: {err}")
    st.stop()

# ------------------------------------------------------------
# CABEÇALHO
# ------------------------------------------------------------
st.markdown("""
<div class="brand"><div class="logo">◎</div><div>
<div class="title">NR-17 | Ergonomia por Visão</div>
<div class="subtitle">MVP 04 — qualidade de captura + ciclos + RULA/REBA no tempo + evidências + eficácia.</div>
</div></div>
""",unsafe_allow_html=True)

st.markdown(f"""
<div class="info-grid">
 <div class="info"><div class="lbl">Setor</div><div class="val">{safe(st.session_state.setor)}</div></div>
 <div class="info"><div class="lbl">Operação / Posto</div><div class="val">{safe(st.session_state.operacao)}</div></div>
 <div class="info"><div class="lbl">Colaborador</div><div class="val">{safe(st.session_state.colaborador)}</div></div>
 <div class="info"><div class="lbl">Turno</div><div class="val">{safe(st.session_state.turno)}</div></div>
 <div class="info"><div class="lbl">Captura</div><div class="val">{safe(camera_profile_name)}</div></div>
</div>
""",unsafe_allow_html=True)

tabs=st.tabs([
    "◉ Acompanhamento",
    "↻ Ciclos & Ângulos",
    "▦ RULA / REBA",
    "▧ Evidências",
    "✓ Plano de ação",
    "⌁ Histórico / Eficácia",
    "▣ Finalizar / PDF",
])
tab_live,tab_cycles,tab_methods,tab_evidence,tab_actions,tab_history,tab_finish=tabs

# ------------------------------------------------------------
# ACOMPANHAMENTO
# ------------------------------------------------------------
with tab_live:
    def render_camera_block():
        st.markdown("""
        <div class="panel"><div class="panel-title">Monitoramento biomecânico</div>
        <div class="panel-sub">Captura otimizada para tablet. Evidências permanecem na resolução recebida; o MediaPipe usa uma cópia reduzida.</div></div>
        """,unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="camera-spec">
              <div><div class="c-label">Câmera preferida</div><div class="c-value">{safe(camera_facing)}</div></div>
              <div><div class="c-label">Solicitado</div><div class="c-value">{camera_profile['width']}×{camera_profile['height']} · {camera_profile['fps']} FPS</div></div>
              <div><div class="c-label">IA</div><div class="c-value">lado máx. {camera_profile['process_long_side']} px</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ctx_local=webrtc_streamer(
            key=f"nr17-v4-{st.session_state.assessment_id}",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=lambda:ErgonomiaVideoProcessor(cfg),
            media_stream_constraints=camera_constraints,
            async_processing=True,
        )

        # 2×2 fica muito mais utilizável em tablet do que quatro botões estreitos.
        b1,b2=st.columns(2)
        with b1:
            if st.button("↺ Zerar",use_container_width=True):
                if ctx_local.video_processor:
                    ctx_local.video_processor.reset(clear_files=True)
                    st.session_state.captured_pose=None
                    st.success("Medição zerada.")
        with b2:
            if st.button("◎ Referência",use_container_width=True):
                if ctx_local.video_processor:
                    snap=ctx_local.video_processor.snapshot()
                    if snap.get("valid_frame"):
                        st.session_state.captured_pose=snap
                        st.success("Postura marcada.")
                    else:
                        st.warning("Aguarde um frame válido.")

        b3,b4=st.columns(2)
        with b3:
            if st.button("▶ Ciclo",use_container_width=True):
                if ctx_local.video_processor:
                    okc,msg=ctx_local.video_processor.start_cycle()
                    (st.success if okc else st.warning)(msg)
        with b4:
            if st.button("■ Fechar ciclo",use_container_width=True):
                if ctx_local.video_processor:
                    okc,msg=ctx_local.video_processor.finish_cycle()
                    (st.success if okc else st.warning)(msg)

        st.caption(
            "Se alterar câmera, resolução, modo de captura, limiares ou fatores RULA/REBA, "
            "pare e inicie novamente a câmera para aplicar as novas configurações."
        )
        return ctx_local

    if layout_mode=="Desktop":
        col_cam,col_data=st.columns([1.48,1.0],gap="large")
        with col_cam:
            ctx=render_camera_block()
        live_target=col_data
    else:
        # No tablet a câmera fica em cima e os indicadores abaixo.
        ctx=render_camera_block()
        live_target=None

    @st.fragment(run_every=1.0)
    def live_panel():
        proc=ctx.video_processor
        if proc is None:
            st.info("Clique em START para iniciar.")
            return
        s=proc.snapshot()

        q=float(s.get("quality",0))
        actual=s.get("resolution","--")
        requested=s.get("requested_resolution",f"{camera_profile['width']}x{camera_profile['height']}")
        processing=s.get("processing_resolution","--")
        orientation=s.get("orientation","--")

        st.markdown(
            f"""<div class="quality-card">
            <div class="small-muted">QUALIDADE DA CAPTURA</div>
            <div style="font-size:1.8rem;font-weight:900;color:{_quality_color(q)}">{q:.0f}% · {_quality_label(q)}</div>
            <div class="small-muted">
                recebida {actual} · solicitada {requested} · IA {processing}<br>
                {s.get('fps',0):.1f} FPS · cobertura {s.get('coverage',0):.0f}% · {safe(orientation)}
            </div>
            </div>""",unsafe_allow_html=True
        )

        if actual!="--" and not s.get("resolution_ok",False):
            st.warning(
                f"O navegador entregou {actual}, abaixo do perfil {requested}. "
                "Confirme câmera traseira principal, use o tablet em paisagem e verifique a qualidade do Wi-Fi."
            )
        elif orientation=="Retrato":
            st.warning("Gire o tablet para paisagem para melhorar o enquadramento biomecânico.")

        if s.get("fps",0) and s.get("fps",0)<18:
            st.warning(
                f"FPS baixo ({s.get('fps',0):.1f}). Se a imagem estiver travando, use o perfil Industrial 720p "
                "ou Econômico 540p."
            )

        if not s.get("valid_frame"):
            msg="Frame descartado: ajuste enquadramento/iluminação"
            if capture_mode!="Visão normal" and not s.get("marker_found"):
                msg=f"Frame descartado: ArUco ID {marker_id} não encontrado"
            st.error(msg)
        else:
            st.success("Frame válido — contabilizando exposição.")

        a,b,c=st.columns(3)
        a.metric("IRE atual",f"{s.get('ire',0)}/100")
        b.metric("RULA ao vivo",f"{s.get('rula',0)}/7")
        c.metric("REBA ao vivo",f"{s.get('reba',0)}/15")

        d,e,f=st.columns(3)
        d.metric("Tempo válido",fmt_seconds(s.get("total_time",0)))
        e.metric("Exposição",f"{s.get('risk_pct',0):.1f}%")
        f.metric("Frames válidos",f"{s.get('valid_pct',0):.1f}%")

        st.markdown("#### Exposição corporal")
        heat=[
            ("Tronco",s.get("trunk_pct",0)),
            ("Pescoço",s.get("neck_pct",0)),
            ("Braço elevado",s.get("arm_pct",0)),
            ("Joelho",s.get("knee_pct",0)),
        ]
        for label,pct in heat:
            st.caption(f"{label} · {pct:.1f}%")
            st.progress(clamp(float(pct)/100,0,1))

        x,y=st.columns(2)
        x.metric("Pior RULA",f"{s.get('max_rula',0)}/7")
        y.metric("Pior REBA",f"{s.get('max_reba',0)}/15")
        st.caption(
            f"RULA predominante {s.get('rula_dominant',0)} · "
            f"REBA predominante {s.get('reba_dominant',0)} · "
            f"{len(s.get('evidence',[]))} evidência(s)"
        )
        if s.get("cycle_active"):
            st.warning("CICLO EM ANDAMENTO")

    if live_target is not None:
        with live_target:
            live_panel()
    else:
        st.markdown("### Indicadores ao vivo")
        live_panel()

# ------------------------------------------------------------
# CICLOS E ÂNGULOS
# ------------------------------------------------------------
with tab_cycles:
    st.markdown("""
    <div class="panel"><div class="panel-title">Ciclo de trabalho e ângulo no tempo</div>
    <div class="panel-sub">Os gráficos usam apenas frames considerados válidos pelo filtro de qualidade.</div></div>
    """,unsafe_allow_html=True)
    proc=ctx.video_processor if 'ctx' in locals() else None
    s=proc.snapshot() if proc else None

    if not s or not s.get("time_series"):
        st.info("Ainda não há dados suficientes. Inicie a câmera e deixe a medição rodar.")
    else:
        df=pd.DataFrame(s["time_series"])
        st.markdown("### Ângulo × tempo")
        angle_cols=[c for c in ["tronco","pescoco","braco_d","braco_e"] if c in df.columns]
        if angle_cols:
            st.line_chart(df.set_index("tempo_s")[angle_cols],height=300)
        st.caption("Valores em graus. A câmera 2D é mais confiável quando o plano de filmagem é compatível com o movimento avaliado.")

        st.markdown("### RULA / REBA × tempo")
        st.line_chart(df.set_index("tempo_s")[["rula","reba"]],height=250)

        c1,c2=st.columns(2)
        with c1:
            st.markdown("#### Distribuição RULA")
            rg=_rula_group_distribution(s.get("rula_seconds",{}))
            for k,v in rg.items():
                st.caption(f"RULA {k} · {v:.1f}%")
                st.progress(clamp(v/100,0,1))
            st.metric("Médio ponderado",f"{s.get('rula_weighted',0):.2f}")
            st.metric("Tempo RULA ≥ 5",f"{s.get('rula_high_pct',0):.1f}%")
        with c2:
            st.markdown("#### Distribuição REBA")
            bg=_reba_group_distribution(s.get("reba_seconds",{}))
            for k,v in bg.items():
                st.caption(f"REBA {k} · {v:.1f}%")
                st.progress(clamp(v/100,0,1))
            st.metric("Médio ponderado",f"{s.get('reba_weighted',0):.2f}")
            st.metric("Tempo REBA ≥ 8",f"{s.get('reba_high_pct',0):.1f}%")

        st.markdown("### Ciclos")
        cycles=s.get("cycles",[])
        if cycles:
            cdf=pd.DataFrame(cycles)
            rename={
                "cycle":"Ciclo","duration":"Duração (s)","risk_pct":"Exposição %",
                "trunk_pct":"Tronco %","neck_pct":"Pescoço %","arm_pct":"Braço %",
                "knee_pct":"Joelho %","max_rula":"RULA máx.","max_reba":"REBA máx.",
                "mean_rula":"RULA médio","mean_reba":"REBA médio",
            }
            st.dataframe(cdf.rename(columns=rename),use_container_width=True,hide_index=True)
        else:
            st.info("Use os botões ▶ Ciclo e ■ Fechar ciclo na aba Acompanhamento.")

# ------------------------------------------------------------
# RULA / REBA
# ------------------------------------------------------------
with tab_methods:
    proc=ctx.video_processor if 'ctx' in locals() else None
    snap=proc.snapshot() if proc else None
    pose=st.session_state.captured_pose or (snap.get("worst_pose") if snap else None)

    st.markdown("""
    <div class="panel"><div class="panel-title">RULA / REBA assistidos</div>
    <div class="panel-sub">O acompanhamento ao vivo já calcula os scores a cada frame válido. Aqui você vê o fechamento da postura de referência ou da pior postura registrada.</div></div>
    """,unsafe_allow_html=True)

    if not pose:
        st.info("Marque uma postura de referência ou deixe o sistema registrar uma postura crítica.")
    else:
        rr=calculate_rula(pose,rula_opts_live)
        rb=calculate_reba(pose,reba_opts_live)
        c1,c2=st.columns(2,gap="large")
        with c1:
            st.markdown(f"""<div class='score-box'><div class='score-number'>{rr['score']}<span style='font-size:1rem;color:#8199b1'>/7</span></div><div class='score-caption'>RULA</div><div class='tag'>{safe(rr['level'])}</div></div>""",unsafe_allow_html=True)
            st.info(rr["action"])
            with st.expander("Detalhamento RULA"):
                st.write(rr)
        with c2:
            st.markdown(f"""<div class='score-box'><div class='score-number'>{rb['score']}<span style='font-size:1rem;color:#8199b1'>/15</span></div><div class='score-caption'>REBA</div><div class='tag'>{safe(rb['level'])}</div></div>""",unsafe_allow_html=True)
            st.info(rb["action"])
            with st.expander("Detalhamento REBA"):
                st.write(rb)

        if snap:
            st.markdown("### Mapa corporal de exposição")
            h1,h2=st.columns(2)
            with h1:
                st.metric("Pescoço",f"{snap.get('neck_pct',0):.1f}%")
                st.metric("Braços",f"{snap.get('arm_pct',0):.1f}%")
            with h2:
                st.metric("Tronco",f"{snap.get('trunk_pct',0):.1f}%")
                st.metric("Joelhos",f"{snap.get('knee_pct',0):.1f}%")

# ------------------------------------------------------------
# EVIDÊNCIAS
# ------------------------------------------------------------
with tab_evidence:
    proc=ctx.video_processor if 'ctx' in locals() else None
    s=proc.snapshot() if proc else {"evidence":[]}
    evidence=s.get("evidence",[])

    st.markdown("""
    <div class="panel"><div class="panel-title">Evidências automáticas</div>
    <div class="panel-sub">A primeira exposição relevante de cada fator gera foto; novos picos podem gerar evidências adicionais respeitando o intervalo configurado.</div></div>
    """,unsafe_allow_html=True)

    if not evidence:
        st.info("Nenhuma evidência registrada.")
    else:
        labels={"TRONCO":"Tronco","PESCOCO":"Pescoço","BRACO":"Braço elevado","JOELHO":"Flexão de joelho"}
        for factor in ["TRONCO","PESCOCO","BRACO","JOELHO"]:
            items=[e for e in evidence if e.get("factor")==factor]
            if not items: continue
            st.markdown(f"### {labels[factor]} · {len(items)}")
            cols=st.columns(min(3,len(items)))
            for i,e in enumerate(items):
                with cols[i%len(cols)]:
                    p=Path(e["path"])
                    if p.exists():
                        st.image(str(p),use_container_width=True)
                        st.caption(
                            f"{e.get('clock','')} · {e.get('value',0):.1f}° · "
                            f"RULA {e.get('rula',0)} · REBA {e.get('reba',0)} · "
                            f"Qualidade {e.get('quality',0):.0f}%"
                        )

# ------------------------------------------------------------
# PLANO DE AÇÃO
# ------------------------------------------------------------
with tab_actions:
    st.markdown("""
    <div class="panel"><div class="panel-title">Plano de ação ergonômico</div>
    <div class="panel-sub">Registre ações vinculadas aos achados. Elas entram no relatório final.</div></div>
    """,unsafe_allow_html=True)

    with st.form("action_form",clear_on_submit=True):
        a1,a2=st.columns(2)
        risk=a1.text_input("Risco / achado",placeholder="Ex.: flexão de tronco durante alimentação")
        action=a2.text_input("Ação proposta",placeholder="Ex.: elevar dispositivo em 150 mm")
        a3,a4,a5=st.columns(3)
        owner=a3.text_input("Responsável")
        deadline=a4.date_input("Prazo")
        status=a5.selectbox("Status",["A fazer","Em andamento","Validar eficácia","Concluído"])
        add=st.form_submit_button("Adicionar ação",use_container_width=True)
        if add and risk.strip() and action.strip():
            st.session_state.actions.append({
                "risk":risk.strip(),"action":action.strip(),"owner":owner.strip(),
                "deadline":deadline.strftime("%d/%m/%Y"),"status":status,
            })
            st.success("Ação adicionada.")

    if st.session_state.actions:
        adf=pd.DataFrame(st.session_state.actions)
        st.dataframe(adf.rename(columns={
            "risk":"Risco / achado","action":"Ação","owner":"Responsável",
            "deadline":"Prazo","status":"Status"
        }),use_container_width=True,hide_index=True)
        if st.button("Limpar plano de ação"):
            st.session_state.actions=[]
            st.rerun()
    else:
        st.info("Nenhuma ação cadastrada.")

# ------------------------------------------------------------
# HISTÓRICO E EFICÁCIA
# ------------------------------------------------------------
with tab_history:
    st.markdown("""
    <div class="panel"><div class="panel-title">Histórico e comparação antes × depois</div>
    <div class="panel-sub">Após salvar avaliações, use uma medição anterior como baseline e compare com a sessão atual.</div></div>
    """,unsafe_allow_html=True)

    proc=ctx.video_processor if 'ctx' in locals() else None
    live=proc.snapshot() if proc else None

    if HISTORY_PATH_V4.exists():
        try:
            hist=pd.read_csv(HISTORY_PATH_V4,sep=";",encoding="utf-8-sig")
            st.dataframe(hist.tail(20),use_container_width=True,hide_index=True)

            ids=hist["avaliacao_id"].astype(str).tolist()
            baseline_id=st.selectbox("Avaliação baseline (ANTES)",ids[::-1])
            base=hist[hist["avaliacao_id"].astype(str)==str(baseline_id)].iloc[-1]

            if live and live.get("total_time",0)>0:
                current_rula=live.get("max_rula",0)
                current_reba=live.get("max_reba",0)
                comparison=pd.DataFrame([
                    ["Exposição geral %",base.get("exposicao_pct",0),live.get("risk_pct",0)],
                    ["Tronco %",base.get("tronco_pct",0),live.get("trunk_pct",0)],
                    ["Braço %",base.get("braco_pct",0),live.get("arm_pct",0)],
                    ["RULA máximo",base.get("rula_max",0),current_rula],
                    ["REBA máximo",base.get("reba_max",0),current_reba],
                ],columns=["Indicador","ANTES","AGORA"])
                comparison["Variação %"]=comparison.apply(
                    lambda r: ((float(r["AGORA"])-float(r["ANTES"]))/float(r["ANTES"])*100)
                    if _safe_num(r["ANTES"])!=0 else 0,
                    axis=1
                )
                st.markdown("### Comparação")
                st.dataframe(comparison,use_container_width=True,hide_index=True)
            else:
                st.info("Inicie uma medição para comparar a sessão atual com o baseline.")
        except Exception as exc:
            st.warning(f"Não foi possível ler o histórico: {exc}")
    else:
        st.info("O histórico V4 será criado ao finalizar a primeira avaliação.")

# ------------------------------------------------------------
# FINALIZAÇÃO / PDF
# ------------------------------------------------------------
with tab_finish:
    proc=ctx.video_processor if 'ctx' in locals() else None
    final_snap=proc.snapshot() if proc else None

    st.markdown("""
    <div class="panel"><div class="panel-title">Fechar avaliação e gerar relatório</div>
    <div class="panel-sub">O PDF consolida identificação, qualidade da captura, exposição, RULA/REBA no tempo, ciclos, ações e evidências.</div></div>
    """,unsafe_allow_html=True)

    missing=[label for label,val in [
        ("Setor",st.session_state.setor),
        ("Operação/Posto",st.session_state.operacao),
        ("Colaborador",st.session_state.colaborador),
    ] if not str(val).strip()]

    if missing:
        st.warning("Preencha: "+", ".join(missing))
    if not final_snap or final_snap.get("total_time",0)<=0:
        st.warning("Ainda não há tempo válido de medição.")

    pose_for_report=None
    rr_final=rb_final=None
    if final_snap:
        pose_for_report=st.session_state.captured_pose or final_snap.get("worst_pose")
        if pose_for_report:
            rr_final=calculate_rula(pose_for_report,rula_opts_live)
            rb_final=calculate_reba(pose_for_report,reba_opts_live)

        m1,m2,m3,m4,m5=st.columns(5)
        m1.metric("Tempo válido",fmt_seconds(final_snap.get("total_time",0)))
        m2.metric("Qualidade média",f"{final_snap.get('quality_avg',0):.0f}%")
        m3.metric("Exposição",f"{final_snap.get('risk_pct',0):.1f}%")
        m4.metric("RULA máx.",f"{final_snap.get('max_rula',0)}/7")
        m5.metric("REBA máx.",f"{final_snap.get('max_reba',0)}/15")

    can_finish=not missing and final_snap and final_snap.get("total_time",0)>0

    if st.button("✓ Finalizar avaliação e gerar PDF",type="primary",use_container_width=True,disabled=not can_finish):
        # fecha ciclo aberto automaticamente
        if proc and final_snap.get("cycle_active"):
            proc.finish_cycle()
            final_snap=proc.snapshot()

        end=datetime.now()
        metadata={
            "avaliacao_id":st.session_state.assessment_id,
            "data":end.strftime("%d/%m/%Y"),
            "inicio":st.session_state.assessment_started.strftime("%H:%M:%S"),
            "fim":end.strftime("%H:%M:%S"),
            "setor":st.session_state.setor,
            "operacao":st.session_state.operacao,
            "colaborador":st.session_state.colaborador,
            "turno":st.session_state.turno,
            "avaliador":st.session_state.avaliador,
            "observacao":st.session_state.observacao,
            "capture_mode":capture_mode,
            "marker_info":f"ID {marker_id}" if capture_mode!="Visão normal" else "Não utilizado",
        }

        pdf_path=REPORT_ROOT/f"relatorio_ergonomia_v4_{st.session_state.assessment_id}.pdf"
        generate_nr17_pdf(
            pdf_path,metadata,final_snap,rr_final,rb_final,
            final_snap.get("evidence",[]),
            critical_pose=pose_for_report,
            cycles=final_snap.get("cycles",[]),
            actions=st.session_state.actions,
        )
        save_record_v4(final_snap,metadata,rr_final,rb_final,pdf_path)
        st.session_state.final_pdf=str(pdf_path)
        st.success("Avaliação finalizada e PDF gerado.")

    if st.session_state.final_pdf and Path(st.session_state.final_pdf).exists():
        p=Path(st.session_state.final_pdf)
        st.download_button("⬇ Baixar relatório PDF",data=p.read_bytes(),file_name=p.name,mime="application/pdf",use_container_width=True)

    if HISTORY_PATH_V4.exists():
        st.download_button("⬇ Baixar histórico V4 CSV",data=HISTORY_PATH_V4.read_bytes(),file_name="historico_nr17_v4.csv",mime="text/csv",use_container_width=True)

    st.divider()
    if st.button("＋ Nova avaliação",use_container_width=True):
        old=st.session_state.assessment_id
        st.session_state.assessment_id=uuid.uuid4().hex[:8].upper()
        st.session_state.assessment_started=datetime.now()
        st.session_state.captured_pose=None
        st.session_state.final_pdf=None
        st.session_state.actions=[]
        st.success(f"Nova avaliação criada. A anterior ({old}) foi preservada.")
        st.rerun()

st.divider()
st.caption(
    "MVP de engenharia. Frames abaixo da qualidade mínima não entram nos indicadores. "
    "RULA/REBA são métodos observacionais assistidos; IRE é um indicador experimental interno. "
    "O sistema não substitui AEP/AET."
)
