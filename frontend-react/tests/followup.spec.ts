import { test, expect } from "@playwright/test";
import type { Conversation, Followup } from "../src/types";

// Isolated browser contract test with API fixtures, not a clinical/LLM evaluation.
for (const choice of ["Não observei", "Não comeu nada", "Comeu a quantidade habitual", "Nenhuma dessas opções descreve o que observei"]) {
  test(`form reload and single submission: ${choice}`, async ({ page }) => {
    const principal = {
      user_id: "followup-test",
      role: "tutor",
      display_name: "Teste",
      demo: true,
      clinic_verified: false,
    };
    const followup: Followup = {
      state: "form",
      question_id: "apetite-1",
      question: "Quanto ele comeu em relação ao habitual?",
      options: [
        "Comeu a quantidade habitual",
        "Comeu menos que o habitual",
        "Não comeu nada",
        "Comeu mais que o habitual",
        "Nenhuma dessas opções descreve o que observei",
        "Não observei",
        "Não sei dizer",
      ],
    };
    const conversation: Conversation = {
      id: "conv-test",
      title: "Gato na caixa",
      pet: null,
      pet_id: null,
      status: "idle",
      error: null,
      updated_at: new Date().toISOString(),
      followup,
      messages: [
        {
          id: "t1",
          role: "tutor",
          content: "Entra na caixa",
          created_at: new Date().toISOString(),
        },
        {
          id: "a1",
          role: "assistant",
          content: "Preciso de mais informação",
          followup,
          created_at: new Date().toISOString(),
          triage: {
            classificacao: "INCERTO",
            justificativa: "Falta informação sobre a urina.",
            sinais_de_alerta: [],
            recomendacao: "Procure orientação veterinária.",
          },
        },
      ],
    };
    const posts: Record<string, string>[] = [];
    await page.addInitScript(
      ({ principal }) => {
        sessionStorage.setItem(
          "vetai.session.v3",
          JSON.stringify({ principal, access_token: "test-token" }),
        );
        sessionStorage.setItem("vetai.chat.followup-test", "conv-test");
      },
      { principal },
    );
    await page.route((url) => url.origin === "http://localhost:8000" || url.pathname.startsWith("/api/"), async (route) => {
      const path = new URL(route.request().url()).pathname.replace(/^\/api\//, "/");
      let body: unknown = [];
      if (path === "/auth/me") body = principal;
      else if (path === "/auth/config") body = {};
      else if (path.endsWith("/messages")) {
        const input = route.request().postDataJSON();
        posts.push(input);
        conversation.messages.push({
          id: input.request_id,
          role: "tutor",
          content: input.content,
          origin: input.origin,
          created_at: new Date().toISOString(),
        });
        conversation.status = "processing";
        body = conversation;
      } else if (path === "/workspace/conversations/conv-test")
        body = conversation;
      else if (path === "/workspace/conversations") body = [conversation];
      await route.fulfill({ json: body });
    });
    await page.goto("/");
    await expect(
      page.getByRole("group", { name: followup.question! }),
    ).toBeVisible();
    await page.reload();
    await page.getByRole("radio", { name: choice, exact: true }).check();
    await page.getByLabel("Complemento (opcional)").fill("Observação do tutor");
    await page
      .getByRole("button", { name: "Enviar resposta", exact: true })
      .evaluate((button: HTMLButtonElement) => {
        button.click();
        button.click();
      });
    await expect(
      page.getByText("Resposta enviada pelo formulário"),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Enviar resposta", exact: true }),
    ).toBeDisabled();
    await expect(
      page.getByText("Analisando seu relato e consultando a base…"),
    ).toBeVisible();
    expect(posts).toHaveLength(1);
    expect(posts[0]).toMatchObject({
      origin: "form",
      question_id: "apetite-1",
      selected_option: choice,
      content: choice + " — Observação do tutor",
    });
    await page.reload();
    await expect(
      page.getByText(choice + " — Observação do tutor", { exact: true }),
    ).toBeVisible();
    expect(posts).toHaveLength(1);
  });
}
