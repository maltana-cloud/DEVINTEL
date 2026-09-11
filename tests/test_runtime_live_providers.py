from devintel.providers import GenerationRequest, GenerationResponse, ProviderHealth, ResearchRequest, ResearchResult
from devintel.runtime.app import DEVINTELRuntime


class Generation:
    provider_id = "runtime-gen"
    def health(self): return ProviderHealth(self.provider_id, True)
    def generate(self, request): return GenerationResponse("generated", self.provider_id)


class Research:
    provider_id = "runtime-research"
    def health(self): return ProviderHealth(self.provider_id, True)
    def search(self, request): return (ResearchResult("https://example.com", "Example"),)


def test_runtime_routes_generation_and_research_without_granting_authority():
    runtime = DEVINTELRuntime()
    runtime.register_generation_provider("runtime-gen", Generation())
    runtime.register_research_provider("runtime-research", Research())
    generated = runtime.generate(GenerationRequest("hello"))
    found = runtime.research(ResearchRequest("hello"))
    assert generated.success and generated.output.text == "generated"
    assert found.success and found.output[0].url == "https://example.com"
    assert runtime.context.state.state.value == "normal"
