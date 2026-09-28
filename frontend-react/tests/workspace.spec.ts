import { test, expect } from "@playwright/test";

// Live local integration tests: no fake API or model responses.
// Use only an isolated academic deployment with quick login enabled.
test("entry, tutor chat, draft restoration and pet persistence", async ({
  page,
}) => {
  const pet = "Teste UI " + Date.now();
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Entrar como tutor" }),
  ).toBeEnabled();
  await page.screenshot({ path: "test-results/entry.png", fullPage: true });
  await page.getByRole("button", { name: "Entrar como tutor" }).click();
  await page
    .getByRole("button", { name: "Nova conversa", exact: true })
    .click();
  await page
    .getByRole("textbox", { name: "Conte o que está acontecendo" })
    .fill("Rascunho de teste, ainda não enviado.");
  await page.reload();
  await expect(
    page.getByRole("textbox", { name: "Conte o que está acontecendo" }),
  ).toHaveValue("Rascunho de teste, ainda não enviado.");
  await page.getByRole("button", { name: "Meus animais", exact: true }).click();
  await page
    .getByRole("button", { name: "Cadastrar animal", exact: true })
    .click();
  await page.getByLabel("Nome do animal").fill(pet);
  await page
    .getByRole("combobox", { name: "Espécie", exact: true })
    .selectOption("gato");
  await page.getByRole("button", { name: "Salvar animal" }).click();
  await expect(page.getByRole("heading", { name: pet })).toBeVisible();
  await page
    .locator(".pet-card")
    .filter({ has: page.getByRole("heading", { name: pet }) })
    .getByRole("button", { name: "Editar informações" })
    .click();
  await page.getByLabel("Peso em kg").fill("4.5");
  await page.getByRole("button", { name: "Salvar animal" }).click();
  await expect(
    page
      .locator(".pet-card")
      .filter({ has: page.getByRole("heading", { name: pet }) }),
  ).toContainText("4.5 kg");
  await page.reload();
  await page.getByRole("button", { name: "Meus animais", exact: true }).click();
  await expect(page.getByRole("heading", { name: pet })).toBeVisible();
  await page
    .getByRole("button", { name: "Nova conversa", exact: true })
    .click();
  await page.getByLabel("Animal desta conversa").selectOption({ label: pet });
  await expect(
    page.getByRole("heading", { name: "Como " + pet + " está hoje?" }),
  ).toBeVisible();
  await page.screenshot({ path: "test-results/chat.png", fullPage: true });
  await page.getByRole("button", { name: "Sair", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Como você quer entrar?" }),
  ).toBeVisible();
});

test("own tutor signup with optional animal persists and logs in again", async ({
  page,
}) => {
  const email = "qa-" + Date.now() + "@example.org";
  const password = "Local-test-only-123!";
  await page.goto("/");
  await page
    .getByRole("button", { name: "Entrar ou cadastrar uma conta própria" })
    .click();
  await page.getByRole("button", { name: "Criar conta", exact: true }).click();
  await page.getByLabel("Seu nome").fill("Pessoa de teste UI");
  await page.getByLabel("E-mail", { exact: true }).fill(email);
  await page.getByLabel("Senha", { exact: true }).fill(password);
  await page.getByLabel("Cadastrar meu animal agora").check();
  await page.getByLabel("Nome do animal").fill("Lua de teste");
  await page
    .getByRole("button", { name: "Criar minha conta", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Nova conversa", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Meus animais", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Lua de teste" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sair", exact: true }).click();
  await page
    .getByRole("button", { name: "Entrar ou cadastrar uma conta própria" })
    .click();
  await page.getByLabel("E-mail", { exact: true }).fill(email);
  await page.getByLabel("Senha", { exact: true }).fill(password);
  await page
    .locator("form")
    .getByRole("button", { name: "Entrar", exact: true })
    .last()
    .click();
  await expect(
    page.getByRole("button", { name: "Nova conversa", exact: true }),
  ).toBeVisible();
});

test("mobile navigation has no horizontal overflow and keeps emergency search accessible", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Entrar como tutor" }).click();
  await page.getByRole("button", { name: "Abrir navegação" }).click();
  await page
    .getByRole("button", { name: "Nova conversa", exact: true })
    .click();
  await expect(
    page.getByRole("textbox", { name: "Conte o que está acontecendo" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/mobile-chat.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Ver clínicas", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Encontre atendimento" }),
  ).toBeVisible();
  await page
    .getByLabel("CEP, endereço ou ponto de referência")
    .fill("Avenida Paulista, São Paulo");
  await page.getByRole("button", { name: "Buscar", exact: true }).click();
  await expect(page.locator(".place-card").first()).toBeVisible({
    timeout: 30000,
  });
  await expect(page.locator(".gm-style")).toBeVisible({ timeout: 30000 });
  await expect(page.locator(".map-overlay")).toHaveCount(0);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/mobile-map.png",
    fullPage: true,
  });
});

test("real stored triage to academic clinic, consent and two-party chat", async ({
  page,
  context,
}) => {
  const conversationId = process.env.LIVE_RAG_CONVERSATION_ID;
  test.skip(
    !conversationId,
    "Set LIVE_RAG_CONVERSATION_ID to a completed real RAG conversation belonging to tutor-a.",
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Entrar como tutor" }).click();
  await page
    .getByRole("button", { name: "Nova conversa", exact: true })
    .waitFor();
  await page.evaluate(
    (id) => sessionStorage.setItem("vetai.chat.demo-tutor-a", id!),
    conversationId,
  );
  await page.reload();
  await expect(page.locator(".triage-card").last()).toBeVisible();
  await page
    .getByRole("button", { name: "Encontrar atendimento", exact: true })
    .first()
    .click();
  await page
    .locator(".academic-unit")
    .filter({ hasText: "Aurora" })
    .getByRole("button", { name: "Compartilhar caso" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Revise antes de enviar" }),
  ).toBeVisible();
  await page
    .getByLabel("Resumo do caso")
    .fill("Caso fictício de validação UI " + Date.now());
  await page
    .getByLabel(
      "Também autorizo compartilhar a conversa completa desta pré-triagem.",
    )
    .check();
  await page
    .getByLabel(
      "Autorizo enviar o resumo, o relato original, a pré-triagem e os dados preenchidos acima para esta clínica.",
    )
    .check();
  await page.getByRole("button", { name: "Confirmar e compartilhar" }).click();
  await expect(
    page.getByRole("heading", { name: "Seu encaminhamento" }),
  ).toBeVisible();
  const clinic = await context.newPage();
  await clinic.goto("/");
  await clinic.getByRole("button", { name: "Entrar como clínica" }).click();
  await expect(
    clinic.getByRole("heading", { name: "Uma visão de quem precisa de você." }),
  ).toBeVisible();
  await clinic.locator(".queue-item").first().click();
  await clinic
    .getByRole("button", { name: "Conversa original", exact: true })
    .click();
  await expect(clinic.locator(".transcript-message").first()).toBeVisible();
  await clinic.getByRole("button", { name: "Aceitar caso" }).click();
  await expect(
    page.getByRole("button", { name: "Estou a caminho" }),
  ).toBeVisible({ timeout: 20000 });
  await page.getByRole("button", { name: "Estou a caminho" }).click();
  await context.grantPermissions(["geolocation"]);
  await context.setGeolocation({ latitude: -23.5614, longitude: -46.6559 });
  await page.getByRole("button", { name: "Autorizar e compartilhar" }).click();
  await expect(
    clinic.getByText("Localização compartilhada", { exact: true }),
  ).toBeVisible({ timeout: 20000 });
  await expect(
    clinic.getByText("Tempo de chegada indisponível", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Interromper e remover posição" })
    .click();
  await expect(
    clinic.getByText("A caminho · sem localização atual", { exact: true }),
  ).toBeVisible({ timeout: 20000 });
  await page
    .getByLabel("Mensagem para a clínica ou tutor")
    .fill("Mensagem de teste do tutor.");
  await page.getByRole("button", { name: "Enviar", exact: true }).click();
  await expect(
    clinic.getByText("Mensagem de teste do tutor.", { exact: true }),
  ).toBeVisible({ timeout: 20000 });
  await clinic
    .getByLabel("Mensagem para a clínica ou tutor")
    .fill("Resposta humana de teste da clínica.");
  await clinic.getByRole("button", { name: "Enviar", exact: true }).click();
  await expect(
    page.getByText("Resposta humana de teste da clínica.", { exact: true }),
  ).toBeVisible({ timeout: 20000 });
  await clinic.screenshot({ path: "test-results/clinic.png", fullPage: true });
  await clinic.getByRole("button", { name: "Registrar chegada" }).click();
  await clinic.getByRole("button", { name: "Concluir caso" }).click();
  await expect(
    page.getByText("Conversa encerrada. O histórico continua disponível."),
  ).toBeVisible({ timeout: 20000 });
});

test("own clinic registration remains pending without exposing patient data", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Entrar ou cadastrar uma conta própria" })
    .click();
  await page.getByRole("button", { name: "Criar conta", exact: true }).click();
  await page.getByLabel("Seu nome").fill("Responsável fictício de teste");
  await page
    .getByRole("combobox", { name: "Perfil", exact: true })
    .selectOption("clinic");
  await page
    .getByLabel("E-mail", { exact: true })
    .fill("clinic-qa-" + Date.now() + "@example.org");
  await page.getByLabel("Senha", { exact: true }).fill("Local-test-only-123!");
  await page
    .getByRole("button", { name: "Criar minha conta", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Solicitar vínculo da clínica" }),
  ).toBeVisible();
  const fields: Record<string, string> = {
    "Nome da unidade": "Unidade fictícia QA",
    "Razão social": "Instituição de teste, sem atendimento",
    "CNPJ / identificação": "00000000000000",
    "Endereço completo": "Endereço fictício de teste",
    Latitude: "-23.5614",
    Longitude: "-46.6559",
    Telefone: "1100000000",
    "Horários declarados": "Sem atendimento — teste",
    "Responsável pela conta": "Responsável fictício",
    "Documento do responsável": "DADO FICTÍCIO",
  };
  for (const [label, value] of Object.entries(fields))
    await page.getByLabel(label, { exact: true }).fill(value);
  await page.getByRole("button", { name: "Enviar para verificação" }).click();
  await expect(
    page.getByRole("heading", { name: "Cadastro em verificação" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Cadastro em verificação" }),
  ).toBeVisible();
  await expect(page.locator(".queue-item")).toHaveCount(0);
});
