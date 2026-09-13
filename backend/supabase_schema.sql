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

-- RLS ligado, mas com política aberta: correto habilitar desde já (é a
-- configuração segura por padrão do Supabase), mas apertar a política
-- exige autenticação de tutor, que ainda não existe (decisão registrada em
-- evidencias/ryu/, "auth mais geral" para a fase de desenvolvimento).
-- ANTES DE QUALQUER USO COM DADOS REAIS DE TUTORES: trocar as políticas
-- abaixo por "tutor só vê o próprio id" quando o login existir.
alter table tutors enable row level security;
alter table pets enable row level security;

create policy "dev: acesso total a tutors"
on tutors for all
using (true)
with check (true);

create policy "dev: acesso total a pets"
on pets for all
using (true)
with check (true);
