use drive;

select *
from user;

select *
from driving;

-- insert into User(ImageSrc)
-- value("db");

-- 마지막으로 추가된 운전자만 셀렉해서 졸음 카운터 할 예정임
update driving
set DrowsyCount = 1
where (select driveorder
		from drive.driving
		order by FirstDrivingTime desc
		limit 1);

-- select *
-- from drive.driving
-- order by FirstDrivingTime desc
-- limit 1;