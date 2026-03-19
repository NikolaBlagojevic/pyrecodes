"""Combine four confusion matrix PNGs into a single 2x2 figure with a, b, c, d labels."""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

IMAGES = [
    'confusion_matrix_baseline.png',
    'confusion_matrix_ruleset.png',
    'confusion_matrix_literature.png',
    'confusion_matrix_gpt5mini.png',
]
LABELS = ['a', 'b', 'c', 'd']
OUTPUT = 'confusion_matrices_combined.png'

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

for ax, filename, label in zip(axes.flat, IMAGES, LABELS):
    img = mpimg.imread(filename)
    ax.imshow(img)
    ax.axis('off')
    ax.text(
        0.5, -0.04,
        f'({label})',
        transform=ax.transAxes,
        ha='center', va='top',
        fontsize=16, fontweight='bold',
    )

plt.tight_layout(h_pad=2, w_pad=1)
plt.savefig(OUTPUT, dpi=300, bbox_inches='tight')
print(f'Saved to {OUTPUT}')
