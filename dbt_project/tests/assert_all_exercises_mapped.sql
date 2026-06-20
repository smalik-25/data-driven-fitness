-- Every exercise in the logs must map to a region (no nulls after the join).
select s.exercise_name
from {{ ref('stg_strong__sets') }} s
left join {{ ref('dim_exercise') }} e using (exercise_name)
where e.region is null
group by s.exercise_name
