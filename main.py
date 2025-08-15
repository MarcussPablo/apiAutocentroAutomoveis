from fastapi import FastAPI, Query
import httpx

app = FastAPI()

API_ORIGINAL = "https://estoque.altimus.com.br/api/estoquejson?estoque=6c1faa70-0f38-46b1-8f54-5a837c404f5e"

@app.get("/api/veiculos")
async def filtrar_veiculos(
    marca: str = Query(None),
    modelo: str = Query(None),
    ano_modelo: int = Query(None, alias="ano.modelo"),  # filtro por ano do modelo
    cor: str = Query(None),
    combustivel: str = Query(None),
    preco_maximo: float = Query(None),
    cambio: str = Query(None),
    formato: str = Query("resumido"),
):
    async with httpx.AsyncClient() as client:
        response = await client.get(API_ORIGINAL)
        dados = response.json()

    veiculos = dados.get("veiculos", [])

    def aplicar_filtros(v):
        if marca and marca.lower() not in v.get("marca", "").lower():
            return False
        if modelo and modelo.lower() not in v.get("modelo", "").lower():
            return False
        if ano_modelo and ano_modelo != v.get("anoModelo"):
            return False
        if cor and cor.lower() not in v.get("cor", "").lower():
            return False
        if combustivel and combustivel.lower() not in v.get("combustivel", "").lower():
            return False
        if preco_maximo and v.get("valorVenda", float('inf')) > preco_maximo:
            return False
        if cambio and cambio.lower() not in v.get("cambio", "").lower():
            return False
        return True

    veiculos_filtrados = list(filter(aplicar_filtros, veiculos))

    if formato == "detalhado":
        return {"veiculos": veiculos_filtrados}
    else:
        resumido = []
        for v in veiculos_filtrados:
            resumido.append({
                "id": v.get("id"),
                "marca": v.get("marca"),
                "modelo": v.get("modelo"),
                "anoFabricacao": v.get("anoFabricacao"),  # mantém ano de fabricação
                "anoModelo": v.get("anoModelo"),          # mantém ano do modelo
                "valorVenda": v.get("valorVenda"),
                "cor": v.get("cor"),
                "combustivel": v.get("combustivel"),
                "cambio": v.get("cambio"),
            })
        return {"veiculos": resumido}
