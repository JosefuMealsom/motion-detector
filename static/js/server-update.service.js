export function updateConfigFileOnServer(url, value) {
  const update = async () => {
    await fetch(url, {
      method: "POST",
      body: JSON.stringify(value),
      headers: { "Content-Type": "application/json" },
    });
  };

  update();
}
