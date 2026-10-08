-- Schema do Supabase (Postgres): identidade do modo real.
--
-- Rode isto uma vez, no SQL Editor do projeto Supabase, depois de criá-lo.
-- O Supabase guarda só os perfis de quem faz login no modo real
-- (WORKFLOW_MODE=real, AUTH_PROVIDER=supabase). Pets, conversas e
-- encaminhamentos ficam no MongoDB do app (workspace).
--
-- Até 06/10/2026 este arquivo também criava as tabelas `tutors` e `pets`, do
-- cadastro antigo da API (rotas /tutors e /pets). O cadastro saiu na rodada
-- 25 do Ryu; este script não as cria mais e também não as apaga: num projeto
-- que já as tenha, removê-las é decisão manual de quem administra o projeto.

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

alter table profiles enable row level security;

drop policy if exists "usuario le o proprio perfil" on profiles;

create policy "usuario le o proprio perfil"
on profiles for select to authenticated
using (user_id = auth.uid());

-- Não há política de UPDATE de role/clinic_verified para o usuário. Essas
-- colunas são administrativas e devem ser alteradas somente com a chave de
-- serviço, após o procedimento manual descrito em docs/segunda-etapa.md.
