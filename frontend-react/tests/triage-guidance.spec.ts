import { test, expect } from "@playwright/test";
import type { Triage } from "../src/types";

// Recorded clinical outputs are fixtures: this suite tests presentation, not accuracy.
for (const classification of ["EMERGENCIA", "INCERTO", "NAO_EMERGENCIA"] as const) {
  test(`supportive guidance preserves ${classification} and original evidence`, async ({ page }) => {
    const principal = { user_id: "guidance-test", role: "tutor", display_name: "Teste", demo: true };
    const triage: Triage = {
      classificacao: classification,
      justificativa: classification === "EMERGENCIA"
        ? "Sua gata apresenta dificuldade respiratoria grave e esta de boca aberta, indicando risco imediato a vida."
        : "Justificativa original preservada.",
      sinais_de_alerta: classification === "NAO_EMERGENCIA"
        ? ["", "  ", "-"]
        : ["", "dificuldade para respirar", " ", "dificuldade para respirar", "boca aberta"],
      recomendacao: "Orientação específica registrada pelo modelo.",
    };
    const conversation = {
      id: "guidance-conversation", title: "Teste de comunicação", status: "idle",
      pet: null, pet_id: null, updated_at: new Date().toISOString(),
      messages: [{ id: "reply", role: "assistant", content: triage.justificativa,
        created_at: new Date().toISOString(), triage }],
    };
    await page.addInitScript(({ principal }) => {
      sessionStorage.setItem("vetai.session.v3", JSON.stringify({ principal, access_token: "fixture" }));
      sessionStorage.setItem("vetai.chat.guidance-test", "guidance-conversation");
    }, { principal });
    await page.route((url) => url.origin === "http://localhost:8000" || url.pathname.startsWith("/api/"), async (route) => {
      const path = new URL(route.request().url()).pathname.replace(/^\/api\//, "/");
      const body = path === "/auth/me" ? principal
        : path === "/auth/config" ? {}
        : path === "/workspace/conversations/guidance-conversation" ? conversation
        : path === "/workspace/conversations" ? [conversation] : [];
      await route.fulfill({ json: body });
    });
    await page.goto("/");
    await expect(page).toHaveTitle(/VetIA/);
    await expect(page.locator(".brand").first()).toContainText("vetia");
    await expect(page.locator(".message-author")).toContainText("VetIA");
    await expect(page.getByText(triage.recomendacao, { exact: true })).toBeVisible();
    await expect(page.locator(".care-steps li")).toHaveCount(2);
    await expect(page.getByText(triage.justificativa, { exact: true })).not.toBeVisible();
    await page.getByText("Ver justificativa original da análise", { exact: true }).click();
    await expect(page.getByText(triage.justificativa, { exact: true })).toBeVisible();
    if (classification === "EMERGENCIA") {
      await expect(page.getByText("Procure atendimento agora", { exact: true })).toBeVisible();
      await expect(page.getByRole("article").getByRole("button", { name: "Encontrar atendimento" })).toBeVisible();
      await expect(page.getByText(/não espere outra resposta aqui/)).toBeVisible();
    } else {
      await expect(page.getByRole("article").getByRole("button", { name: "Encontrar atendimento" })).toHaveCount(0);
    }
    if (classification === "INCERTO") {
      await expect(page.getByText(/isso não significa que esteja tudo bem/)).toBeVisible();
    }
    if (classification === "NAO_EMERGENCIA") {
      await expect(page.locator(".reported-signs")).toHaveCount(0);
    } else {
      await expect(page.locator(".reported-signs")).toHaveText(
        "Sinais identificados no relato: dificuldade para respirar; boca aberta.");
    }
    await page.setViewportSize({ width: 390, height: 844 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.getByText("Ver justificativa original da análise", { exact: true }).click();
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: test.info().outputPath("guidance-mobile.png"), fullPage: true });
  });
}
