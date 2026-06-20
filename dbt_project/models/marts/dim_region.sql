-- DEXA body regions used for training-volume roll-ups. Grain: one region.
select * from (values
    ('arms',  'Biceps, triceps, deltoids (shoulders assigned to arms per owner)'),
    ('legs',  'Quads, hamstrings, glutes, calves, adductors, abductors'),
    ('trunk', 'Chest, back, abs, traps, lower back')
) as t(region, description)
