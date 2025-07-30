import pandas as pd

class SetupSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # At the beginning of each request, load from session into globals
        from cook_for_kids.globals import Setup  # Import your Setup class

        # Initialize session from globals if session doesn't exist
        if 'setup_df' not in request.session:
            # Use existing global value or default
            if hasattr(Setup, 'df') and Setup.df is not None:
                request.session['setup_df'] = Setup.df.to_dict()
            else:
                request.session['setup_df'] = pd.DataFrame().to_dict()


        if 'setup_optimise' not in request.session:
            # Use existing global value or default
            if hasattr(Setup, 'optimise'):
                request.session['setup_optimise'] = True
            else:
                request.session['setup_optimise'] = True

        if 'setup_trial_number' not in request.session:
            # Use existing global value or default
            if hasattr(Setup, 'trial_number'):
                request.session['setup_trial_number'] = Setup.trial_number
            else:
                request.session['setup_trial_number'] = 1000


        # Load from session to globals (this preserves session state across requests)
        Setup.df = pd.DataFrame(request.session['setup_df'])
        Setup.optimise = request.session['setup_optimise']
        Setup.trial_number = request.session['setup_trial_number']

        # Process the request
        response = self.get_response(request)

        # After the request, save globals back to session
        request.session['setup_df'] = Setup.df.to_dict() if Setup.df is not None else {}
        request.session['setup_optimise'] = Setup.optimise
        request.session['setup_trial_number'] = Setup.trial_number

        return response
