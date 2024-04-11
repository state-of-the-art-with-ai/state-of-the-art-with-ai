
class SummaryFormatter:
    def format(self, source: str):
        """
        return keywords from project descriptions

        :return:
        """

        prompt = f"""Your task is to properly format a blog post to be pbulished form a unformatted source
return the articles as markdown links, find the best spacing arrangement psosssible between the articles. Mkae it very readable

blog post content starts###{{text}}
###content ends

formatted blogpost content starts###{{text}}
        """
        from state_of_the_art.llm import LLM
        result = LLM().call(prompt, source)
        return result

if __name__ == "__main__":
    import fire
    fire.Fire()