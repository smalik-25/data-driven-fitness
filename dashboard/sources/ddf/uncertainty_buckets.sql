-- Long format for the stacked decomposition bar.
with t as (select lean_delta from mart_dexa_change where region = 'total')
select 'Observed lean Δ' as bar, '1 · Plausible newbie muscle' as component,
       least(lean_delta, 4.29) as lbs from t
union all
select 'Observed lean Δ', '2 · Glycogen / hydration water',
       round(lean_delta - least(lean_delta, 4.29), 2) from t
