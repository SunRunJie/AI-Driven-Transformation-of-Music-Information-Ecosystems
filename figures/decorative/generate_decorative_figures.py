"""
Decorative figure generation script
====================================
Generates decorative conceptual figures in PNG format for the industry case study
research report.

Output directory: output/figures/decorative/
Dependencies: pip install matplotlib numpy

Usage:
    python generate_decorative_figures.py

The placement of each figure in the report is described in README.md
"""

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# ===== Font configuration =====
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 200

OUTPUT_DIR = Path(__file__).parent


def save(fig, filename):
    """Save a figure to the output directory"""
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"  [OK] {filename}")
    plt.close(fig)


# ================================================================
# Figure A: Value chain
# ================================================================
def fig_value_chain():
    """Music Information Service Value Chain (corresponds to Section 1.1.1 of the report)"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Define node positions
    nodes = {
        'Creation': (0.5, 0.85),
        'Distribution': (0.5, 0.70),
        'Streaming': (0.25, 0.55),
        'Sales': (0.75, 0.55),
        'Information Aggregation': (0.5, 0.40),
        'Curatorial Decisions': (0.5, 0.22),
        'Listening': (0.30, 0.08),
        'Purchase': (0.70, 0.08),
    }

    # Draw nodes
    colors = {
        'Creation': '#5a9a6a', 'Distribution': '#5a9a6a',
        'Streaming': '#7aba8a', 'Sales': '#7aba8a',
        'Information Aggregation': '#4a90d9', 'Curatorial Decisions': '#e8a838',
        'Listening': '#7a7aba', 'Purchase': '#7a7aba',
    }

    for name, (x, y) in nodes.items():
        box = mpatches.FancyBboxPatch(
            (x - 0.08, y - 0.04), 0.16, 0.08,
            boxstyle="round,pad=0.015",
            facecolor=colors[name], edgecolor='#333', linewidth=1.2
        )
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=9,
                color='white' if name != 'Curatorial Decisions' else 'white',
                fontweight='bold')

    # Draw arrows
    arrow_style = dict(arrowstyle='->', color='#555', lw=1.5)
    ax.annotate('', xy=(0.5, 0.70), xytext=(0.5, 0.81), arrowprops=arrow_style)
    ax.annotate('', xy=(0.25, 0.55), xytext=(0.5, 0.66), arrowprops=arrow_style)
    ax.annotate('', xy=(0.75, 0.55), xytext=(0.5, 0.66), arrowprops=arrow_style)
    ax.annotate('', xy=(0.5, 0.40), xytext=(0.5, 0.51), arrowprops=arrow_style)
    ax.annotate('', xy=(0.5, 0.22), xytext=(0.5, 0.36), arrowprops=arrow_style)
    ax.annotate('', xy=(0.30, 0.08), xytext=(0.40, 0.20), arrowprops=arrow_style)
    ax.annotate('', xy=(0.70, 0.08), xytext=(0.60, 0.20), arrowprops=arrow_style)
    # Feedback loop
    ax.annotate('', xy=(0.5, 0.91), xytext=(0.30, 0.12),
                arrowprops=dict(arrowstyle='->', color='#aaa', lw=1, linestyle='dashed'))
    ax.annotate('', xy=(0.5, 0.91), xytext=(0.70, 0.12),
                arrowprops=dict(arrowstyle='->', color='#aaa', lw=1, linestyle='dashed'))

    # Annotations
    ax.text(0.5, 0.32, '← Trust Infrastructure Layer →', ha='center', va='center',
            fontsize=8, color='#4a90d9', style='italic')
    ax.text(0.50, 0.94, 'Music Creation', ha='center', fontsize=7, color='#888')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Figure A  Music Information Service Value Chain', fontsize=13, fontweight='bold', pad=10)

    return fig


# ================================================================
# Figure B: Evolution timeline
# ================================================================
def fig_evolution_timeline():
    """Evolution Timeline (corresponds to Section 1.1.2 of the report)"""
    fig, ax = plt.subplots(figsize=(10, 4.5))

    stages = [
        ('Web 1.0\nStatic Databases\n1990s-2004', 0.12, '#7a7aba',
         'AllMusic editorial curation\nExpert-driven, one-way flow'),
        ('Web 2.0\nUGC Explosion\n2005-2015', 0.37, '#4a90d9',
         'RYM/AOTY crowdsourced ratings\nData + institutional asset accumulation'),
        ('Mobile + Algorithms\n2015-2022', 0.62, '#5a9a6a',
         'Rise of algorithmic recommendation\nTraffic growth, trust concerns'),
        ('Generative AI Shock\nLate 2022 - present', 0.87, '#d94a4a',
         'Near-zero-cost AI content\nLegitimacy crisis of the rating system'),
    ]

    for label, x, color, desc in stages:
        # Main node circles
        circle = plt.Circle((x, 0.5), 0.10, facecolor=color, edgecolor='#333',
                            linewidth=1.5, alpha=0.9)
        ax.add_patch(circle)
        ax.text(x, 0.5, label, ha='center', va='center', fontsize=6.5,
                color='white', fontweight='bold')

        # Description text
        ax.text(x, 0.25, desc, ha='center', va='top', fontsize=7,
                color='#444', linespacing=1.5)

    # Connecting arrows
    for i in range(len(stages) - 1):
        x1 = stages[i][1] + 0.10
        x2 = stages[i + 1][1] - 0.10
        ax.annotate('', xy=(x2, 0.5), xytext=(x1, 0.5),
                    arrowprops=dict(arrowstyle='->', color='#bbb', lw=2))

    # Timeline main axis
    ax.plot([0.02, 0.98], [0.5, 0.5], color='#ccc', lw=1, zorder=0)

    ax.set_xlim(0, 1)
    ax.set_ylim(0.1, 0.9)
    ax.axis('off')
    ax.set_title('Figure B  Evolution of Music Information Service Platforms', fontsize=13, fontweight='bold', pad=10)

    return fig


# ================================================================
# Figure C: Traditional UGC flywheel vs. AI reverse flywheel
# ================================================================
def fig_flywheel_compare():
    """Traditional UGC Flywheel vs. AI Reverse Flywheel (corresponds to Section 2.2.2 of the report)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    # Left: traditional UGC flywheel
    steps_pos = ['User Creation', 'Gaining Recognition', 'Reputation Growth', 'Sustained Creation', 'Content Accumulation', 'Platform Value Growth']
    colors_pos = ['#4a9a5a', '#5aaa6a', '#6aba7a', '#7aca8a', '#8ada9a', '#9aeaaa']

    for i, (step, c) in enumerate(zip(steps_pos, colors_pos)):
        angle = -i * 60 + 90
        x = 0.5 + 0.30 * np.cos(np.radians(angle))
        y = 0.5 + 0.30 * np.sin(np.radians(angle))
        circle = plt.Circle((x, y), 0.10, facecolor=c, edgecolor='#2a6a3a',
                            linewidth=1.2, alpha=0.9)
        ax1.add_patch(circle)
        ax1.text(x, y, step, ha='center', va='center', fontsize=7,
                 color='#222' if i >= 4 else 'white', fontweight='bold')

    # Circular arrows
    for i in range(6):
        a1 = -i * 60 + 90
        a2 = -(i + 1) * 60 + 90
        x1 = 0.5 + 0.30 * np.cos(np.radians(a1))
        y1 = 0.5 + 0.30 * np.sin(np.radians(a1))
        x2 = 0.5 + 0.30 * np.cos(np.radians(a2))
        y2 = 0.5 + 0.30 * np.sin(np.radians(a2))
        ax1.annotate('', xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color='#2a6a3a', lw=1.5))

    ax1.text(0.5, 0.08, 'Positive incentive cycle', ha='center', fontsize=8, color='#2a6a3a')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    ax1.set_title('Traditional UGC Flywheel', fontsize=11, fontweight='bold')

    # Right: AI reverse flywheel
    steps_neg = ['AI Mass Production', 'Signal-to-Noise Deterioration', 'Genuine Content Buried', 'Creator Exit', 'Quality Decline', 'Platform Devaluation']
    colors_neg = ['#d94a4a', '#e05a5a', '#e76a6a', '#ee7a7a', '#f58a8a', '#fc9a9a']

    for i, (step, c) in enumerate(zip(steps_neg, colors_neg)):
        angle = i * 60 + 90
        x = 0.5 + 0.30 * np.cos(np.radians(angle))
        y = 0.5 + 0.30 * np.sin(np.radians(angle))
        circle = plt.Circle((x, y), 0.10, facecolor=c, edgecolor='#8f2a2a',
                            linewidth=1.2, alpha=0.9)
        ax2.add_patch(circle)
        ax2.text(x, y, step, ha='center', va='center', fontsize=7,
                 color='#222' if i >= 4 else 'white', fontweight='bold')

    for i in range(6):
        a1 = i * 60 + 90
        a2 = (i + 1) * 60 + 90
        x1 = 0.5 + 0.30 * np.cos(np.radians(a1))
        y1 = 0.5 + 0.30 * np.sin(np.radians(a1))
        x2 = 0.5 + 0.30 * np.cos(np.radians(a2))
        y2 = 0.5 + 0.30 * np.sin(np.radians(a2))
        ax2.annotate('', xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color='#8f2a2a', lw=1.5))

    ax2.text(0.5, 0.08, 'Reverse vicious cycle', ha='center', fontsize=8, color='#8f2a2a')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    ax2.set_title('Reverse Flywheel Under AI Impact', fontsize=11, fontweight='bold')

    fig.suptitle('Figure C  Comparison of UGC Incentive Structures', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()

    return fig


# ================================================================
# Figure D: Causal chain of four institutional logics
# ================================================================
def fig_four_dimensions():
    """Causal Chain of Four Institutional Logics (corresponds to Section 2.2.2 of the report)"""
    fig, ax = plt.subplots(figsize=(10, 3.5))

    layers = [
        ('Technology Layer\nDisruption of Information Production', '#4a90d9',
         '• Production costs approach zero\n• Quality distribution normalizes\n• Supply elasticity becomes infinite'),
        ('Institutional Layer\nRedistribution of Rating Authority', '#d9a84a',
         '• Identity admission mechanisms fail\n• Lemons market dynamics\n• Trust-to-noise ratio deteriorates'),
        ('Organizational Layer\nGenerational Upgrade of Service Functions', '#5a9a6a',
         '• Defensive: trust maintenance\n• Offensive: value creation\n• Institutional: rule redesign'),
        ('Value Layer\nRevaluation of Data Assets', '#9a5aaa',
         '• Use up, scarcity down\n• Certification up, transactions down\n• From scale to credibility'),
    ]

    for i, (title, color, content) in enumerate(layers):
        x = 0.12 + i * 0.24
        # Title box
        title_box = mpatches.FancyBboxPatch(
            (x - 0.10, 0.62), 0.20, 0.30,
            boxstyle="round,pad=0.05",
            facecolor=color, edgecolor='#333', linewidth=1.5
        )
        ax.add_patch(title_box)
        ax.text(x, 0.77, title, ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')

        # Content box
        content_box = mpatches.FancyBboxPatch(
            (x - 0.10, 0.08), 0.20, 0.50,
            boxstyle="round,pad=0.05",
            facecolor='#f8f8f8', edgecolor=color, linewidth=1.2
        )
        ax.add_patch(content_box)
        ax.text(x, 0.33, content, ha='center', va='center', fontsize=7,
                color='#444', linespacing=1.6)

        # Arrow
        if i < 3:
            ax.annotate('', xy=(x + 0.14, 0.77), xytext=(x + 0.12, 0.77),
                        arrowprops=dict(arrowstyle='->', color='#888', lw=2))

    # Causality annotations
    ax.text(0.12, 0.96, '(Cause)', ha='center', fontsize=7, color='#888')
    ax.text(0.36, 0.96, '(Transmission)', ha='center', fontsize=7, color='#888')
    ax.text(0.60, 0.96, '(Response)', ha='center', fontsize=7, color='#888')
    ax.text(0.84, 0.96, '(Outcome)', ha='center', fontsize=7, color='#888')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Figure D  Four Institutional Logics Under AI Impact', fontsize=13, fontweight='bold', pad=10)

    return fig


# ================================================================
# Figure E: Lemons market mechanism
# ================================================================
def fig_lemons_market():
    """Lemons Market Mechanism (corresponds to Section 2.2.2, Dimension 2 of the report)"""
    fig, ax = plt.subplots(figsize=(9, 4))

    # Three regions
    regions = [
        (0.15, 0.70, 'Pre-AI Era', '#4a9a5a',
         ['Genuine human ratings', 'Users trust the system by default', 'High-quality ratings earn reputation']),
        (0.50, 0.70, 'AI Shock Process', '#d9a84a',
         ['AI-generated fake signals', 'Rising screening costs', 'Declining signal credibility']),
        (0.85, 0.70, 'Lemons Outcome', '#d94a4a',
         ['High-value signals crowded out', 'Low-quality content expands', 'Platform value damaged']),
    ]

    for x, y, title, color, items in regions:
        # Region title
        ax.text(x, y, title, ha='center', va='center', fontsize=10,
                color=color, fontweight='bold')

        # Item list
        for j, item in enumerate(items):
            ax.text(x, y - 0.15 - j * 0.13, f'• {item}', ha='center',
                    va='center', fontsize=7.5, color='#444')

        # Region box
        rect = mpatches.FancyBboxPatch(
            (x - 0.22, y - 0.55), 0.44, 0.60,
            boxstyle="round,pad=0.05",
            facecolor='none', edgecolor=color, linewidth=1.5, linestyle='--'
        )
        ax.add_patch(rect)

    # Arrows
    ax.annotate('', xy=(0.38, 0.70), xytext=(0.30, 0.70),
                arrowprops=dict(arrowstyle='->', color='#888', lw=2))
    ax.annotate('', xy=(0.73, 0.70), xytext=(0.65, 0.70),
                arrowprops=dict(arrowstyle='->', color='#888', lw=2))

    # Lemma annotation
    ax.text(0.50, 0.08, 'Akerlof (1970) lemons market theory: when buyers cannot distinguish good goods from lemons, good goods leave the market',
            ha='center', fontsize=7, color='#888', style='italic')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Figure E  Lemons Mechanism of the Rating Market', fontsize=13, fontweight='bold', pad=10)

    return fig


# ================================================================
# Figure F: Trust literacy pyramid
# ================================================================
def fig_trust_pyramid():
    """Trust Literacy Capability Pyramid (corresponds to Section 5.2.1 of the report)"""
    fig, ax = plt.subplots(figsize=(8, 5.5))

    layers = [
        (0.50, 0.78, 0.70, 0.14, 'Trust Architecture Capability', '#d94a4a',
         'Systematic understanding of technology-institution-business interactions\nAbility to design trustworthy systems'),
        (0.50, 0.58, 0.80, 0.18, 'Institutional Design and Governance', '#d9a84a',
         'Reputation system design · Community rule design\nHuman-AI collaborative processes · Incentive mechanism design'),
        (0.50, 0.36, 0.88, 0.18, 'Discrimination and Verification Capability', '#4a90d9',
         'AI content detection · Statistical anomaly detection\nData provenance techniques · Adversarial analysis'),
        (0.50, 0.12, 0.95, 0.20, 'Interdisciplinary Knowledge Foundation', '#5a9a6a',
         'Information economics · Institutional economics · Computational social science\nAI/ML fundamentals · Platform governance'),
    ]

    for x, y, width, height, title, color, desc in layers:
        # Trapezoid (approximated with a rectangle)
        box = mpatches.FancyBboxPatch(
            (x - width / 2, y - height / 2), width, height,
            boxstyle="round,pad=0.03",
            facecolor=color, edgecolor='#333', linewidth=1.2, alpha=0.9
        )
        ax.add_patch(box)
        ax.text(x, y + 0.02, title, ha='center', va='center', fontsize=10,
                color='white', fontweight='bold')
        ax.text(x, y - 0.06, desc, ha='center', va='center', fontsize=7,
                color='white' if title == 'Trust Architecture Capability' else '#222',
                linespacing=1.3)

    # Arrows
    for i in range(3):
        y_pos = [0.12, 0.36, 0.58][i] + 0.10
        ax.annotate('', xy=(0.50, [0.28, 0.48, 0.68][i]),
                    xytext=(0.50, y_pos),
                    arrowprops=dict(arrowstyle='->', color='#aaa', lw=1.5))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Figure F  Trust Literacy Capability Model', fontsize=13, fontweight='bold', pad=10)

    return fig


# ================================================================
# Figure G: Career development roadmap
# ================================================================
def fig_career_path():
    """Career Development Roadmap (corresponds to Section 5.1.1 of the report)"""
    fig, ax = plt.subplots(figsize=(9, 4.5))

    stages = [
        (0.15, 0.20, 'Entry Stage\n0-2 years', '#8aba9a',
         ['Data Analyst', 'Community Operations Specialist', 'Content Moderator']),
        (0.40, 0.40, 'Growth Stage\n3-5 years', '#6a9ada',
         ['AI Content Discriminator', 'Platform Governance Specialist', 'Authenticity Auditor']),
        (0.65, 0.60, 'Mature Stage\n5-10 years', '#d9a84a',
         ['Trust Architect', 'Head of Governance', 'Independent Consultant']),
        (0.88, 0.80, 'Expert Stage\n10+ years', '#d94a4a',
         ['Chief Trust Officer\nIndustry Standard Setter']),
    ]

    for x, y, label, color, roles in stages:
        # Stage node
        circle = plt.Circle((x, y), 0.10, facecolor=color, edgecolor='#333',
                            linewidth=1.5, alpha=0.9)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=7,
                color='white', fontweight='bold')

        # Role list
        for j, role in enumerate(roles):
            ax.text(x, y - 0.16 - j * 0.12, f'• {role}', ha='center',
                    va='center', fontsize=6.5, color='#444')

    # Upward arrows
    ax.annotate('', xy=(0.38, 0.32), xytext=(0.17, 0.17),
                arrowprops=dict(arrowstyle='->', color='#888', lw=2))
    ax.annotate('', xy=(0.63, 0.52), xytext=(0.42, 0.38),
                arrowprops=dict(arrowstyle='->', color='#888', lw=2))
    ax.annotate('', xy=(0.86, 0.73), xytext=(0.67, 0.58),
                arrowprops=dict(arrowstyle='->', color='#888', lw=2))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Figure G  Career Development Path in the Trust Economy', fontsize=13, fontweight='bold', pad=10)

    return fig


# ================================================================
# Figure H: Trust threshold curve
# ================================================================
def fig_trust_curve():
    """Trust Threshold Curve (corresponds to Section 8.1, Conclusion 2 of the report)"""
    fig, ax = plt.subplots(figsize=(8, 4.5))

    # S-shaped trust curve
    p = np.linspace(0, 1, 200)
    alpha, beta = 0.55, 6.0
    trust = 1.0 / (1.0 + np.exp(beta * (p - alpha)))

    ax.plot(p * 100, trust, 'b-', linewidth=2.5, label='User trust T(p)')

    # Annotate the inflection point
    turning_point = alpha
    ax.axvline(x=turning_point * 100, color='#d9a84a', linestyle='--', linewidth=1.5,
               alpha=0.8)
    ax.text(turning_point * 100 + 1, 0.5, f'Inflection point {turning_point * 100:.1f}%',
            fontsize=8, color='#d9a84a', rotation=90)

    # Annotate the collapse point
    collapse_point = 0.75
    ax.axvline(x=collapse_point * 100, color='#d94a4a', linestyle='--', linewidth=1.5,
               alpha=0.8)
    ax.text(collapse_point * 100 + 1, 0.5, f'Collapse point {collapse_point * 100:.0f}%',
            fontsize=8, color='#d94a4a', rotation=90)

    # Trust threshold line
    threshold = 0.4
    ax.axhline(y=threshold, color='#888', linestyle=':', linewidth=1, alpha=0.6)
    ax.text(102, threshold, 'Trust threshold', fontsize=7, color='#888')

    # Shade the collapse region
    ax.axvspan(collapse_point * 100, 100, alpha=0.08, color='#d94a4a')

    ax.set_xlabel('AI content penetration rate (%)', fontsize=10)
    ax.set_ylabel('User trust', fontsize=10)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    ax.set_title('Figure H  Trust Threshold Curve: Nonlinear Collapse of Trust', fontsize=13, fontweight='bold')

    return fig


# ================================================================
# Figure I: Strategic positioning in the competitive landscape
# ================================================================
def fig_competitive_map():
    """Strategic Positioning in the Competitive Landscape (corresponds to Section 3.2.1 of the report)"""
    fig, ax = plt.subplots(figsize=(8, 7))

    platforms = {
        'RYM': (9.5, 7.0, 5, '#4a90d9'),
        'AOTY': (7.0, 8.5, 3, '#5aaa6a'),
        'Pitchfork': (5.0, 3.0, 2, '#d9a84a'),
        'Discogs': (9.0, 5.0, 15, '#e88a3a'),
        'Bandcamp': (6.0, 6.5, 20, '#9a5aaa'),
        'Spotify': (3.0, 4.0, 500, '#1DB954'),
        'Apple Music': (3.0, 3.0, 350, '#e84a4a'),
        'Douban Music': (6.5, 7.0, 8, '#e84a8a'),
        'Last.fm': (8.0, 5.0, 10, '#d94a4a'),
    }

    for name, (x, y, size, color) in platforms.items():
        s = np.sqrt(size) * 12
        ax.scatter(x, y, s=s, c=color, alpha=0.7, edgecolors='#333',
                   linewidth=0.8, zorder=5)
        offset = 0.25 if size < 20 else 0.4
        ax.text(x, y + offset, name, ha='center', va='center', fontsize=8,
                fontweight='bold', color='#333')

    # Quadrant division
    ax.axhline(y=5.5, color='#ccc', linestyle='--', linewidth=0.8)
    ax.axvline(x=5.5, color='#ccc', linestyle='--', linewidth=0.8)

    # Quadrant labels
    ax.text(8.0, 8.0, 'High social, high data', fontsize=8, color='#888', style='italic')
    ax.text(3.0, 8.0, 'High social, low data', fontsize=8, color='#888', style='italic')
    ax.text(8.0, 2.0, 'Low social, high data', fontsize=8, color='#888', style='italic')
    ax.text(3.0, 2.0, 'Low social, low data', fontsize=8, color='#888', style='italic')

    ax.set_xlabel('Data depth', fontsize=11)
    ax.set_ylabel('Social experience', fontsize=11)
    ax.set_xlim(2, 10)
    ax.set_ylim(2, 9.5)
    ax.set_title('Figure I  Competitive Positioning of Music Information Service Platforms', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.15)

    return fig


# ================================================================
# Figure J: Strategic response matrix
# ================================================================
def fig_strategy_matrix():
    """Strategic Response Matrix (corresponds to Section 2.2.2, Dimension 3 of the report)"""
    fig, ax = plt.subplots(figsize=(7, 6))

    strategies = [
        (0.25, 0.75, 'Defensive', 'Trust maintenance', '#4a90d9',
         'AI content detection\nRating authenticity index\nHuman review system'),
        (0.75, 0.75, 'Offensive', 'Value creation', '#5a9a6a',
         'AI curation assistant\nPersonalized discovery\nData licensing services'),
        (0.25, 0.25, 'Institutional', 'Rule redesign', '#d9a84a',
         'Rater certification system\nBlockchain notarization\nCommunity self-governance mechanisms'),
        (0.75, 0.25, 'Ecosystem', 'Boundary expansion', '#9a5aaa',
         'Open API\nDeveloper ecosystem\nParticipation in industry standards'),
    ]

    for x, y, label, sub, color, content in strategies:
        box = mpatches.FancyBboxPatch(
            (x - 0.20, y - 0.20), 0.40, 0.40,
            boxstyle="round,pad=0.05",
            facecolor=color, edgecolor='#333', linewidth=1.5, alpha=0.85
        )
        ax.add_patch(box)
        ax.text(x, y + 0.10, label, ha='center', va='center', fontsize=11,
                color='white', fontweight='bold')
        ax.text(x, y + 0.02, sub, ha='center', va='center', fontsize=8,
                color='white', alpha=0.9)
        ax.text(x, y - 0.08, content, ha='center', va='center', fontsize=7,
                color='white', linespacing=1.4)

    # Axis annotations
    ax.text(0.50, 0.01, 'Long-term layout ———————→', ha='center', fontsize=8, color='#888')
    ax.text(0.01, 0.50, '← Defense-first', va='center', fontsize=8, color='#888',
            rotation=90)
    ax.text(0.99, 0.50, 'Offense-first →', va='center', fontsize=8, color='#888',
            rotation=90)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Figure J  Platform Strategic Response Matrix', fontsize=13, fontweight='bold', pad=10)

    return fig


# ================================================================
# Figure K: Heterogeneous trust across generations
# ================================================================
def fig_heterogeneous_trust():
    """Heterogeneous Trust Curves of Four User Types (corresponds to Section 2.2.1 of the report)"""
    fig, ax = plt.subplots(figsize=(8, 4.5))

    p = np.linspace(0, 1, 200)
    user_types = [
        ('Veteran music fans (β=4.0)', 4.0, 0.55, '#d94a4a'),
        ('Active users (β=2.5)', 2.5, 0.55, '#d9a84a'),
        ('Ordinary users (β=1.2)', 1.2, 0.55, '#4a90d9'),
        ('Casual browsers (β=0.6)', 0.6, 0.55, '#5a9a6a'),
    ]

    for label, beta, alpha, color in user_types:
        trust = 1.0 / (1.0 + np.exp(beta * (p - alpha)))
        ax.plot(p * 100, trust, linewidth=2, label=label, color=color)

    ax.axhline(y=0.5, color='#888', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.text(102, 0.5, 'Trust threshold\n(T=0.5)', fontsize=7, color='#888')

    ax.set_xlabel('AI content penetration rate (%)', fontsize=10)
    ax.set_ylabel('User trust', fontsize=10)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=8, loc='lower left')
    ax.set_title('Figure K  Heterogeneous Trust Curves of Four User Types', fontsize=13, fontweight='bold')

    return fig


# ================================================================
# Figure L: Data asset value paradox
# ================================================================
def fig_data_value_paradox():
    """The Dual Value Paradox of Data Assets (corresponds to Section 2.2.2, Dimension 4 of the report)"""
    fig, ax = plt.subplots(figsize=(8, 4))

    categories = ['Use value', 'Scarcity value', 'Certification value', 'Transaction value']
    effects = [0.6, -0.7, 0.8, -0.5]  # positive/negative effects

    bars = ax.bar(categories, effects, width=0.5,
                  color=['#5a9a6a' if e > 0 else '#d94a4a' for e in effects],
                  edgecolor='#333', linewidth=1.2, alpha=0.85)

    # Annotate values
    for bar, e in zip(bars, effects):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (0.05 if e > 0 else -0.08),
                f'{e:+.1f}', ha='center', fontsize=10, fontweight='bold',
                color='#5a9a6a' if e > 0 else '#d94a4a')

    # Explanatory text
    ax.text(0.5, -0.25,
            'The "dual value paradox" of data assets in the AI era: use value and certification value rise,\nscarcity value and transaction value fall; the net effect depends on the platform\'s certification capability',
            ha='center', fontsize=7.5, color='#666',
            transform=ax.transData, linespacing=1.5)

    ax.axhline(y=0, color='#333', linewidth=0.8)
    ax.set_ylabel('AI shock effect (positive/negative)', fontsize=10)
    ax.set_ylim(-1.0, 1.2)
    ax.set_title('Figure L  Revaluation of Data Assets', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.15, axis='y')

    return fig


# ================================================================
# Main function
# ================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("  Generating decorative figures...")
    print("=" * 50)

    generators = [
        ('fig_value_chain.png', fig_value_chain, 'Figure A  Value Chain'),
        ('fig_evolution_timeline.png', fig_evolution_timeline, 'Figure B  Evolution Timeline'),
        ('fig_flywheel_compare.png', fig_flywheel_compare, 'Figure C  Flywheel Comparison'),
        ('fig_four_dimensions.png', fig_four_dimensions, 'Figure D  Four Logics'),
        ('fig_lemons_market.png', fig_lemons_market, 'Figure E  Lemons Market'),
        ('fig_trust_pyramid.png', fig_trust_pyramid, 'Figure F  Trust Literacy'),
        ('fig_career_path.png', fig_career_path, 'Figure G  Career Path'),
        ('fig_trust_curve.png', fig_trust_curve, 'Figure H  Trust Curve'),
        ('fig_competitive_map.png', fig_competitive_map, 'Figure I  Competitive Positioning'),
        ('fig_strategy_matrix.png', fig_strategy_matrix, 'Figure J  Strategy Matrix'),
        ('fig_heterogeneous_trust.png', fig_heterogeneous_trust, 'Figure K  Heterogeneous Trust'),
        ('fig_data_value_paradox.png', fig_data_value_paradox, 'Figure L  Value Paradox'),
    ]

    for filename, gen_func, desc in generators:
        print(f"\n  Generating {desc}...")
        try:
            fig = gen_func()
            save(fig, filename)
        except Exception as e:
            print(f"  [FAIL] {filename} failed: {e}")

    print("\n" + "=" * 50)
    print(f"  Done! {len(generators)} figures generated")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 50)
