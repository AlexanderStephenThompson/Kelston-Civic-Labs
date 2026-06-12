# Query Cookbook

`kelston generate` builds `data/kelston.db`; `kelston query "<SQL>"` runs
read-only SQL against it. Tables are the short schema names (citizen,
dwelling, growing_plot, ...), references are id columns, and every row
carries its `conforms_to` stamp. A few favorites - all verified against
the seed-42 town.

## Nobody fights their own biology

Nocturnal citizens and the shifts they actually work:

```sql
SELECT c.active_hours_preference AS preferred, a.shift_band AS works, COUNT(*) AS n
FROM appointment a
JOIN citizen c ON c.id = a.citizen
JOIN species_profile s ON s.id = c.species
WHERE s.activity_cycle = 'nocturnal'
GROUP BY 1, 2 ORDER BY n DESC;
```

Almost everyone nocturnal works the night band - and the handful of
day-band rows are the owls with day jobs (preferences are the citizen's
own, not the species').

## Housing guarantees, audited

Every household's largest member against their home's clearance - returns
zero rows, because the standard is enforced:

```sql
SELECT h.id FROM household h
JOIN dwelling d ON d.id = h.dwelling
JOIN citizen c ON c.household = h.id
JOIN species_profile s ON s.id = c.species
WHERE
  CASE d.clearance_class WHEN 'tiny' THEN 0 WHEN 'small' THEN 1
       WHEN 'medium' THEN 2 WHEN 'large' THEN 3 ELSE 4 END
  <
  CASE s.size_class WHEN 'tiny' THEN 0 WHEN 'small' THEN 1
       WHEN 'medium' THEN 2 WHEN 'large' THEN 3 ELSE 4 END;
```

## Who tends the submerged paddies

```sql
SELECT g.id, s.common_name AS steward_species
FROM growing_plot g
JOIN citizen c ON c.id = g.steward
JOIN species_profile s ON s.id = c.species
WHERE g.vertical_tier = 'submerged';
```

Harbor seals and capybaras - never a citizen the water would not suit,
because `submerged_plots_need_semi_aquatic_steward` is a validated
constraint, not a hiring custom.

## Harvest, realm by realm

```sql
SELECT r.name AS realm, ROUND(SUM(h.yield_mass)) AS kilograms
FROM harvest_record h
JOIN planting p ON p.id = h.planting
JOIN growing_plot g ON g.id = p.plot
JOIN realm r ON r.id = g.realm
GROUP BY 1 ORDER BY kilograms DESC;
```

## Ectotherm housing, kept warm

Reptile-citizen homes by climate provision (Drylands homes may be ambient -
the realm itself provides):

```sql
SELECT r.name AS realm, d.climate_provision, COUNT(DISTINCT c.id) AS reptile_residents
FROM citizen c
JOIN species_profile s ON s.id = c.species
JOIN household h ON h.id = c.household
JOIN dwelling d ON d.id = h.dwelling
JOIN realm r ON r.id = d.realm
WHERE s.thermoregulation = 'ectotherm'
GROUP BY 1, 2 ORDER BY 1, 3 DESC;
```

## From plot to plate

The whole food loop in one row per delivery:

```sql
SELECT dr.delivered_on, fr.name AS farm, rv.name AS variety,
       ml.lot_mass, dest.name AS delivered_to
FROM distribution_run dr
JOIN market_lot ml ON ml.id = dr.lot
JOIN harvest_record hr ON hr.id = ml.harvest
JOIN planting p ON p.id = hr.planting
JOIN crop_variety rv ON rv.id = p.variety
JOIN farm fr ON fr.id = ml.seller
JOIN realm dest ON dest.id = dr.destination_realm
ORDER BY dr.delivered_on LIMIT 10;
```

## What version is this record?

```sql
SELECT conforms_to, COUNT(*) FROM growing_plot GROUP BY 1;
```

One stamp, town-wide - and after a standards change, `kelston upgrade`
keeps it that way.
