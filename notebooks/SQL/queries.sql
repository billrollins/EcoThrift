------------------------------------------
select 
    count(*)
from 
    public.home_order a
inner join public.home_item b
    on a.id = b.order_id;

------------------------------------------
select distinct
    a.id, a.order_number
from 
    public.home_order a
inner join public.home_item b
    on a.id = b.order_id
where b.status = '';


------------------------------------------