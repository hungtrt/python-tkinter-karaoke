create table customer
(
	id int auto_increment
		primary key,
	name varchar(50) not null,
	type char(10) not null,
	phone char(12) null,
	address varchar(100) null,
	customer_incentives int not null,
	amount_consumed bigint not null,
	created_date timestamp not null,
	updated_date timestamp null
);

create table room
(
	id char(10) not null
		primary key,
	name varchar(50) not null,
	volume int not null,
	description varchar(100) null,
	status varchar(20) not null
);

create table booking_room
(
	id int auto_increment
		primary key,
	id_room varchar(10) not null,
	id_customer int not null,
	created_date timestamp not null,
	ended_time timestamp null,
	updated_date timestamp null,
	constraint booking_room_customer_id_fk
		foreign key (id_customer) references customer (id),
	constraint booking_room_room_id_fk
		foreign key (id_room) references room (id)
);

create table bill
(
	id int auto_increment
		primary key,
	id_booking_room int not null,
	created_date timestamp not null,
	constraint bill_booking_room_id_fk
		foreign key (id_booking_room) references booking_room (id)
);

create table room_rates
(
	id char(10) not null
		primary key,
	id_room char(10) not null,
	unit_price bigint not null,
	description varchar(200) null,
	time_slot int null,
	constraint room_rates_room_id_fk
		foreign key (id_room) references room (id)
);

create table service
(
	id char(10) not null
		primary key,
	name varchar(50) not null,
	unit varchar(20) not null,
	unit_price bigint not null
);

create table service_detail
(
	id int auto_increment
		primary key,
	id_service char(10) not null,
	quantity int not null,
	created_date timestamp not null,
	updated_date timestamp null,
	booking_room_id int null,
	constraint service_detail_booking_room_id_fk
		foreign key (booking_room_id) references booking_room (id),
	constraint service_detail_service_id_fk
		foreign key (id_service) references service (id)
);


