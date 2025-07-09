from matrx_orm.sql_executor import register_query, execute_query, list_available_queries, generate_documentation, get_query_details
import database_project_config
from matrx_utils import vcprint


def register_all_queries():

    register_query(name="get_latest_scraped_pages", query={
        "query": """
        WITH latest_pages AS (
            SELECT DISTINCT ON (page_name) *
            FROM public.scrape_parsed_page
            WHERE page_name = ANY(%(page_names)s)
            AND (expires_at IS NULL OR expires_at > NOW())
            AND scraped_at IS NOT NULL
            ORDER BY page_name, scraped_at DESC
        )
        SELECT * FROM latest_pages
        ORDER BY scraped_at DESC
        """,
        "params": [
            {
                "name": "page_names",
                "required": True,
                "description": "List of page names to retrieve",
                "type": "string[]",
                "default": None
            }
        ],
        "database": "supabase_automation_matrix",
        "description": "Get the latest non-expired scraped pages for a list of page names, sorted by scraped_at descending",
        "example": "execute_query('get_latest_scraped_pages', {'page_names': ['mailchimp_com_solutions_email_marketing_platform', 'mailchimp_com_solutions_email_marketing_subscribe']})",
        "executor_type": "standard"
    })


def main():

    # Use the complex query
    results = execute_query('get_latest_scraped_pages', {
        'page_names': ['mailchimp_com_solutions_email_marketing_platform', 'mailchimp_com_solutions_email_marketing_subscribe']
    })

    print(f"Found {len(results)} scraped pages")
    for page in results:
        vcprint(page, color="bright_pink")


if __name__ == "__main__":

    register_all_queries()
    vcprint(generate_documentation(), color="bright_pink")
    input("Press Enter to continue...")
    main()
