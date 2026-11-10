import { test, expect, type Page } from "@playwright/test";

// Histórico do animal como contexto da análise (rodada 34 do João).
// Integração local de verdade, sem API falsa. A leitura usa o modelo local,
// que aproveita o texto do PDF sem chamar modelo nenhum: o teste não gasta
// cota e dá sempre o mesmo resultado.
const PDF = "tests/fixtures/exame-ficticio.pdf";

async function entrarComAnimal(page: Page, animal: string) {
  const email = "qa-doc-" + Date.now() + "@example.org";
  await page.goto("/");
  await page
    .getByRole("button", { name: "Entrar ou cadastrar uma conta própria" })
    .click();
  await page.getByRole("button", { name: "Criar conta", exact: true }).click();
  await page.getByLabel("Seu nome").fill("Pessoa de teste de documentos");
  await page.getByLabel("E-mail", { exact: true }).fill(email);
  await page.getByLabel("Senha", { exact: true }).fill("Local-test-only-123!");
  await page.getByLabel("Cadastrar meu animal agora").check();
  await page.getByLabel("Nome do animal").fill(animal);
  await page
    .getByRole("button", { name: "Criar minha conta", exact: true })
    .click();
  await expect(
    page.getByRole("textbox", { name: "Conte o que está acontecendo" }),
  ).toBeVisible();
}

async function anexar(page: Page) {
  await page
    .getByRole("combobox", { name: "Provedor da análise" })
    .selectOption("ollama");
  await page
    .locator(".composer input[type=file][accept*=pdf]")
    .setInputFiles(PDF);
  await expect(page.getByText("Ler “exame-ficticio.pdf”?")).toBeVisible();
  await expect(page.getByText("lido no servidor local")).toBeVisible();
  await page.getByRole("button", { name: "Ler documento" }).click();
  await expect(page.getByText("Confira o que foi lido")).toBeVisible();
}

test("tutor anexa um documento, revisa o resumo e ele vira contexto do animal", async ({
  page,
}) => {
  const animal = "Mel de teste";
  await entrarComAnimal(page, animal);
  await page
    .getByLabel("Animal desta conversa")
    .selectOption({ label: animal });
  await anexar(page);
  const resumo = page.locator(".document-review textarea");
  await expect(resumo).toHaveValue(/Creatinina/);
  // O tutor revisa: tira os dados pessoais e deixa o que importa.
  await page.getByLabel("Tipo de documento").fill("Exame de sangue");
  await page.locator(".document-fields input").nth(1).fill("02/11/2026");
  await resumo.fill(
    "Creatinina 2,9 mg/dL e ureia 112 mg/dL, altas. Doença renal crônica. Usa benazepril. Alergia a dipirona.",
  );
  await page.screenshot({ path: "test-results/document-review.png" });
  await page.getByRole("button", { name: "Guardar resumo" }).click();
  const contexto = page.locator(".records-list");
  await expect(contexto.locator("summary")).toHaveText(
    "Contexto de " + animal + " na análise: 1 documento",
  );
  await contexto.locator("summary").click();
  await expect(contexto).toContainText("Exame de sangue · 02/11/2026");
  await expect(contexto).toContainText("Alergia a dipirona");
  await page.screenshot({ path: "test-results/document-context.png" });

  // O documento é do animal: aparece em "Meus animais" e numa conversa nova.
  await page.getByRole("button", { name: "Meus animais", exact: true }).click();
  const cartao = page.locator(".pet-card").filter({ hasText: animal });
  await expect(cartao.locator(".records-list summary")).toContainText(
    "1 documento",
  );
  await page
    .getByRole("button", { name: "Nova conversa", exact: true })
    .click();
  await page
    .getByLabel("Animal desta conversa")
    .selectOption({ label: animal });
  await expect(page.locator(".chat-page .records-list summary")).toHaveText(
    "Contexto de " + animal + " na análise: 1 documento",
  );

  // Remover tira do contexto.
  await page.getByRole("button", { name: "Meus animais", exact: true }).click();
  await cartao.locator(".records-list summary").click();
  await cartao.getByRole("button", { name: "Remover Exame de sangue" }).click();
  await expect(cartao.locator(".records-list")).toHaveCount(0);
});

test("sem animal associado, o documento vale só para a conversa", async ({
  page,
}) => {
  await entrarComAnimal(page, "Outro animal");
  await anexar(page);
  await page.getByRole("button", { name: "Descartar" }).click();
  await expect(page.locator(".document-review")).toHaveCount(0);
  await anexar(page);
  await page.getByRole("button", { name: "Guardar resumo" }).click();
  await expect(page.locator(".chat-page .records-list summary")).toHaveText(
    "Contexto desta conversa na análise: 1 documento",
  );
  await page
    .getByRole("button", { name: "Nova conversa", exact: true })
    .click();
  await expect(page.locator(".chat-page .records-list")).toHaveCount(0);
});

test("no celular, anexar e revisar cabem na tela, sem rolagem horizontal", async ({
  page,
}) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await entrarComAnimal(page, "Mel no celular");
  await anexar(page);
  const semRolagem = () =>
    page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    );
  expect(await semRolagem()).toBeTruthy();
  // O cartão de revisão abre à vista, abaixo do cabeçalho preso.
  const topo = await page
    .locator(".document-review")
    .evaluate((e) => e.getBoundingClientRect().top);
  expect(topo).toBeGreaterThanOrEqual(70);
  expect(topo).toBeLessThan(400);
  await page.screenshot({ path: "test-results/document-review-mobile.png" });
  await page.getByRole("button", { name: "Guardar resumo" }).click();
  await expect(page.locator(".chat-page .records-list summary")).toBeVisible();
  expect(await semRolagem()).toBeTruthy();
  await page.screenshot({ path: "test-results/document-context-mobile.png" });
});
