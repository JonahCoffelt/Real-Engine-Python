import pygame as pg

def load_sheet():
    ui_sheet_img = pg.image.load('UI_Assets\card_sheet.png').convert_alpha()
    ui_surfaces = []

    w, h = ui_sheet_img.get_rect()[2:]

    for y1 in range(h):
        for x1 in range(w):
            color = tuple(ui_sheet_img.get_at((x1, y1)))
            if not color == (255, 0, 0, 255): continue
            x2, y2 = x1, y1
            while tuple(ui_sheet_img.get_at((x2, y1))) != (0, 255, 0, 255): x2 += 1
            while tuple(ui_sheet_img.get_at((x2, y2))) != (0, 0, 255, 255): y2 += 1
            surf = pg.Surface((x2 - x1 - 1, y2 - y1 - 1)).convert_alpha()
            surf.fill((0, 0, 0, 0))
            surf.blit(ui_sheet_img, (-x1 - 1, -y1 - 1))
            ui_surfaces.append(surf)
    
    return ui_surfaces