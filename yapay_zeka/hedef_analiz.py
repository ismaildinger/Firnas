def sapma_hesapla(frame_width, x1, x2):
    center = frame_width // 2
    hedef = (x1 + x2) // 2
    sapma = hedef - center
    if abs(sapma) < 20:
        return "STOP", sapma
    return ("LEFT" if sapma > 0 else "RIGHT"), sapma