
DELETE FROM media WHERE code = '8967';
DELETE FROM media WHERE code = 'MCFT';
DELETE FROM media WHERE code = 'BBRK';
DELETE FROM media WHERE title = 'Капитан Америка';
DELETE FROM media WHERE code = 'WTCH';
DELETE FROM media WHERE code = '4863';

SELECT * FROM media WHERE title LIKE '%Stranger Things (2016)%' OR code = '9755';
SELECT * FROM media WHERE title LIKE '%Dune: Part Two (2024)%' OR code = '9538';
SELECT * FROM media WHERE title LIKE '%Пушки Акимбо%' OR code = 'MCTF';
SELECT * FROM media WHERE title LIKE '%Во все тяжкие%';
SELECT * FROM media WHERE title LIKE '%Новый мир%';
SELECT * FROM media WHERE title LIKE '%Два холма%';
SELECT * FROM media WHERE title LIKE '%Урок%';
SELECT * FROM media WHERE title LIKE '%Жизнь по вызову%';
SELECT * FROM media WHERE title LIKE '%Кухня%';


UPDATE media
SET title = 'Про это самое'
WHERE title = 'Stranger Things (2016)';

UPDATE media
SET title = 'Бесстыжие'
WHERE title = 'Dune: Part Two (2024)';

UPDATE media
SET description = 'Молодой врач-сексолог приезжает работать в родное село. Дерзкая комедия о борьбе с предрассудками'
WHERE code = '9755';

UPDATE media
SET description = 'Комедийная драма о многодетной семье Галлагеров, живущей в нищете на юге Чикаго. Отец — алкоголик, дети выживают как могут. Сериал полон чёрного юмора, жизненных ситуаций и социальной критики.'
WHERE code = '9538';

UPDATE media
SET description = 'Драма о слепом полковнике в отставке (Аль Пачино), который решает оторваться на выходных перед тем, как покончить с собой. Его сопровождает молодой студент. Фильм о жизни, чести и выборе.'
WHERE code = '8662';

UPDATE media
SET description = 'Брутальный экшен с элементами сатиры. Главный герой (Дэниел Рэдклифф) просыпается с прикрученными к рукам пистолетами и вынужден участвовать в смертельной игре, транслируемой в прямом эфире.'
WHERE code = '3965';

UPDATE media
SET description = 'Поэтичная историческая драма о первых колонистах в Америке и встрече Джона Смита с индейской принцессой Покахонтас. Картина полна визуальной красоты и философских размышлений о культуре и цивилизации.'
WHERE code = '4863';

UPDATE media
SET description = 'Один из самых культовых сериалов. Учитель химии превращается в производителя метамфетамина после диагноза «рак». История о падении человека, выборе и последствиях.'
WHERE code = '0357';

UPDATE media
SET description = 'Российский фантастический сериал о постапокалиптическом будущем, где мужчины и женщины живут в изоляции друг от друга. Персонажи с двух холмов сталкиваются, и начинается конфликт и поиск взаимопонимания.'
WHERE code = '2015';

UPDATE media
SET description = 'Остросоциальный драматический сериал о молодом учителе, пришедшем в обычную школу с желанием изменить систему изнутри. Он сталкивается с цинизмом, равнодушием и насилием — как со стороны учеников, так и коллег. Это не просто история о школе, а жесткое высказывание о сегодняшнем обществе, где уроки получают не только дети, но и взрослые.'
WHERE code = '4100';

UPDATE media
SET description = 'Сериал о девушках, работающих в сфере эскорта. Показывает внутреннюю кухню индустрии, психологию клиенток и работников, а также цену красивой жизни.'
WHERE code = '9340';

UPDATE media
SET description = 'Комедийный сериал о ресторане Claude Monet, его эксцентричном шефе, официантах, поварах и веселой, но напряжённой жизни за кулисами элитного ресторана. Один из самых успешных российских ситкомов.'
WHERE code = '1598';
