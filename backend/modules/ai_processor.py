"""
Processador de IA usando Google Gemini
"""
import google.generativeai as genai
from ..config import settings
from ..database import db
from typing import Dict, Any, List, Optional
import logging
import hashlib
import json
import tiktoken

logger = logging.getLogger(__name__)

# Configurar Gemini
genai.configure(api_key=settings.secure_google_ai_api_key)

class AIProcessor:
    def __init__(self):
        self.model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self._embedding_cache = {}  # Cache simples para embeddings
    
    def count_tokens(self, text: str) -> int:
        """Conta tokens no texto"""
        return len(self.encoding.encode(text))
    
    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding do texto com cache"""
        try:
            # Limitar tamanho do texto para embeddings
            if len(text) > 2000:
                text = text[:2000] + "..."
            
            # Verificar cache
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self._embedding_cache:
                return self._embedding_cache[text_hash]
            
            result = genai.embed_content(
                model=f"models/{settings.EMBEDDING_MODEL}",
                content=text,
                task_type="retrieval_document",
                title="Conteúdo RecifeMais"
            )
            
            embedding = result['embedding']
            
            # Salvar no cache (limitado a 1000 entradas)
            if len(self._embedding_cache) < 1000:
                self._embedding_cache[text_hash] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    def create_editorial_prompt(self, email_content: str, similar_content: List[Dict] = None) -> str:
        """Cria prompt editorial para o Gemini"""
        
        # Contexto editorial do RecifeMais
        editorial_context = """
        CONTEXTO EDITORIAL RECIFEMAIS:
        
        IDENTIDADE: "Alma e Pulso" - Conectar o Recife à sua essência e energia
        PÚBLICO: "Conectado Recifense" - Pessoas que amam Recife e querem se manter informadas
        
        VALORES FUNDAMENTAIS:
        - Autenticidade recifense
        - Informação útil e confiável  
        - Proximidade com a comunidade
        - Valorização da cultura local
        - Responsabilidade social
        
        CATEGORIAS PRINCIPAIS:
        - Notícias: Tom confiável e preciso
        - Cultura: Tom inspirador e apaixonado
        - Gastronomia: Tom acolhedor e descritivo
        - Turismo: Tom convidativo e informativo
        - Economia: Tom analítico mas acessível
        - Eventos: Tom animado e engajador
        """
        
        # Contexto de conteúdo similar (RAG)
        rag_context = ""
        if similar_content:
            rag_context = "\n\nCONTEÚDO RELACIONADO EXISTENTE:\n"
            for content in similar_content[:3]:  # Limitar a 3 para não sobrecarregar
                rag_context += f"- {content.get('topic', 'Sem título')}: {content.get('content_text', '')[:200]}...\n"
        
        prompt = f"""
        {editorial_context}
        
        {rag_context}
        
        TAREFA: Transforme este email de assessoria em um post otimizado para RecifeMais.
        
        EMAIL:
        {email_content[:1500]}  # Limitar para economizar tokens
        
        INSTRUÇÕES RÁPIDAS:
        - Categoria: noticia, cultura, gastronomia, turismo, economia ou evento
        - Título SEO: máx 60 caracteres, com palavra-chave
        - Meta: máx 155 caracteres, atrativa
        - Conteúdo: foco no público recifense, linguagem clara
        - Tags: 3-5 tags relevantes
        - Score: 1-10 (relevância para RecifeMais)
        
        RESPOSTA JSON:
        {{
            "categoria": "categoria",
            "titulo": "título_seo_60_chars",
            "meta_descricao": "meta_155_chars",
            "conteudo": "post_completo_formatado",
            "tags": ["tag1", "tag2", "tag3"],
            "relevancia_score": 8.5,
            "observacoes": "breve_comentario"
        }}
        """
        
        return prompt
    
    def process_email_content(self, email_content: str, email_hash: str) -> Optional[Dict[str, Any]]:
        """Processa conteúdo do email com IA"""
        try:
            # Gerar embedding para busca de conteúdo similar
            embedding = self.generate_embedding(email_content)
            similar_content = []
            
            if embedding:
                similar_content = db.search_similar_content(embedding, limit=3)
            
            # Criar prompt editorial
            prompt = self.create_editorial_prompt(email_content, similar_content)
            
            # Contar tokens
            input_tokens = self.count_tokens(prompt)
            
            if input_tokens > settings.MAX_TOKENS_PER_REQUEST:
                logger.warning(f"Prompt muito longo: {input_tokens} tokens")
                # Truncar email se necessário
                email_content = email_content[:2000] + "..."
                prompt = self.create_editorial_prompt(email_content, similar_content)
                input_tokens = self.count_tokens(prompt)
            
            # Gerar resposta
            response = self.model.generate_content(prompt)
            
            if not response.text:
                logger.error("Resposta vazia do Gemini")
                return None
            
            # Contar tokens de saída
            output_tokens = self.count_tokens(response.text)
            
            # Tentar parsear JSON
            try:
                # Limpar resposta se tiver markdown
                clean_response = response.text.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:-3]
                elif clean_response.startswith("```"):
                    clean_response = clean_response[3:-3]
                
                parsed_response = json.loads(clean_response)
            except json.JSONDecodeError:
                logger.error("Erro ao parsear JSON da resposta")
                # Fallback: retornar resposta crua
                parsed_response = {
                    "categoria": "indefinida",
                    "titulo": "Conteúdo processado pela IA",
                    "conteudo": response.text,
                    "observacoes": "Resposta não estruturada - necessita revisão manual"
                }
            
            # Calcular custo aproximado (valores estimados)
            cost_per_1k_input = 0.00015  # $0.15 per 1K input tokens
            cost_per_1k_output = 0.0006  # $0.60 per 1K output tokens
            
            estimated_cost = (input_tokens / 1000 * cost_per_1k_input) + (output_tokens / 1000 * cost_per_1k_output)
            
            return {
                "parsed_response": parsed_response,
                "raw_response": response.text,
                "prompt_used": prompt,
                "tokens_input": input_tokens,
                "tokens_output": output_tokens,
                "estimated_cost": estimated_cost,
                "similar_content_found": len(similar_content)
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento de IA: {e}")
            return None
    
    def suggest_proactive_topics(self, seed_topics: List[str] = None) -> List[Dict[str, Any]]:
        """Sugere pautas proativas baseadas em tendências"""
        
        if not seed_topics:
            seed_topics = [
                "eventos em Recife",
                "gastronomia pernambucana", 
                "turismo no Recife",
                "cultura recifense",
                "desenvolvimento urbano Recife"
            ]
        
        prompt = f"""
        CONTEXTO: Você é um especialista em conteúdo para RecifeMais, portal de notícias de Recife.
        
        TAREFA: Sugira 5 pautas originais e atrativas sobre Recife, baseadas nos temas: {', '.join(seed_topics)}
        
        CRITÉRIOS:
        - Relevantes para o público recifense
        - Potencial de engajamento alto
        - Oportunidades de SEO
        - Originalidade e criatividade
        - Conexão com a identidade "Alma e Pulso"
        
        FORMATO DE RESPOSTA (JSON):
        {{
            "pautas": [
                {{
                    "titulo": "título_da_pauta",
                    "resumo": "resumo_executivo",
                    "categoria": "categoria_sugerida",
                    "keywords_seo": ["palavra1", "palavra2"],
                    "formato_sugerido": "artigo/lista/guia/video",
                    "potencial_engajamento": 8.5,
                    "justificativa": "por_que_essa_pauta_é_relevante"
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            if response.text:
                clean_response = response.text.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:-3]
                elif clean_response.startswith("```"):
                    clean_response = clean_response[3:-3]
                
                parsed = json.loads(clean_response)
                return parsed.get("pautas", [])
            
        except Exception as e:
            logger.error(f"Erro ao sugerir pautas: {e}")
        
        return []

# Instância global
ai_processor = AIProcessor() 