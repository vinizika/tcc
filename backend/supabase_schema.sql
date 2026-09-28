-- Schema do Supabase (Postgres) para tutores e pets.
--
-- Rode isto uma vez, no SQL Editor do projeto Supabase, depois de criá-lo.
-- Corresponde a app/schemas/tutor.py e app/schemas/pet.py — mudar um lado
-- sem o outro quebra TutorService/PetService (app/services/).

create extension if not exists "pgcrypto";

create table if not exists tutors (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    phone text,
    email text,
    created_at timestamptz not null default now()
);

-- Migração segura: registros antigos permanecem preservados, mas não são
-- associados a uma conta por semelhança de nome/e-mail. Um administrador só
-- preenche user_id depois de verificar a identidade do titular.
alter table tutors add column if not exists user_id uuid unique references auth.users(id) on delete set null;

create table if not exists pets (
    id uuid primary key default gen_random_uuid(),
    tutor_id uuid not null references tutors(id) on delete cascade,
    name text not null,
    species text not null check (species in ('cao', 'gato')),
    breed text,
    sex text check (sex in ('macho', 'femea')),
    neutered boolean,
    birth_date date,
    weight_kg numeric(5, 2) check (weight_kg > 0 and weight_kg <= 150),
    vaccination_up_to_date boolean,
    last_vaccination_date date,
    chronic_conditions text,
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists pets_tutor_id_idx on pets (tutor_id);

-- updated_at muda sozinho a cada UPDATE; PetService nunca escreve nele.
create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists pets_set_updated_at on pets;

create trigger pets_set_updated_at
before update on pets
for each row execute function set_updated_at();

-- Identidade da segunda etapa. O perfil nasce tutor por padrão. Solicitar o
-- papel clínica não concede verificação nem acesso operacional: clinic_id e
-- clinic_verified só são preenchidos pelo procedimento administrativo.
create table if not exists profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    display_name text not null,
    role text not null check (role in ('tutor', 'clinic')) default 'tutor',
    clinic_id text,
    clinic_verified boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create or replace function create_profile_for_auth_user()
returns trigger as $$
begin
    insert into public.profiles (user_id, display_name, role)
    values (
        new.id,
        coalesce(new.raw_user_meta_data ->> 'display_name', split_part(new.email, '@', 1)),
        case when new.raw_user_meta_data ->> 'requested_role' = 'clinic' then 'clinic' else 'tutor' end
    ) on conflict (user_id) do nothing;
    return new;
end;
$$ language plpgsql security definer set search_path = public;

drop trigger if exists auth_user_created_profile on auth.users;
create trigger auth_user_created_profile
after insert on auth.users
for each row execute function create_profile_for_auth_user();

alter table tutors enable row level security;
alter table pets enable row level security;
alter table profiles enable row level security;

drop policy if exists "dev: acesso total a tutors" on tutors;
drop policy if exists "dev: acesso total a pets" on pets;
drop policy if exists "tutor gerencia o proprio cadastro" on tutors;
drop policy if exists "tutor gerencia os proprios pets" on pets;
drop policy if exists "usuario le o proprio perfil" on profiles;

create policy "tutor gerencia o proprio cadastro"
on tutors for all to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

create policy "tutor gerencia os proprios pets"
on pets for all to authenticated
using (exists (select 1 from tutors where tutors.id = pets.tutor_id and tutors.user_id = auth.uid()))
with check (exists (select 1 from tutors where tutors.id = pets.tutor_id and tutors.user_id = auth.uid()));

create policy "usuario le o proprio perfil"
on profiles for select to authenticated
using (user_id = auth.uid());

-- Não há política de UPDATE de role/clinic_verified para o usuário. Essas
-- colunas são administrativas e devem ser alteradas somente com a chave de
-- serviço, após o procedimento manual descrito em docs/segunda-etapa.md.
