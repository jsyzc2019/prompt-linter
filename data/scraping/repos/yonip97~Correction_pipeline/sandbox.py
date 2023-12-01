
import openai

def get_chatgpt_response(model,input, max_length, **kwargs):
    openai.api_key = "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"
    try:
        message = [{
            "role": "user",
            "content": input,
        }]
        response = openai.ChatCompletion.create(
            model=model,
            messages=message,
            temperature=0,
            max_tokens=max_length
        )
        return response['choices'][0]['message']['content']
    except openai.OpenAIError as e:
        print(f"Error occurred: {e}")
        return None

model = 'gpt-4'
input = """
Please review the provided summary and edit it for factual consistency while minimizing changes to the original content. Ensure that the revised summary accurately represents the information in the original text
Original text:
Paul Merson has restarted his row with Andros Townsend after the Tottenham midfielder was brought on with only seven minutes remaining in his team's 0-0 draw with Burnley on Sunday. 'Just been watching the game, did you miss the coach? #RubberDub #7minutes,' Merson put on Twitter. Merson initially angered Townsend for writing in his Sky Sports column that 'if Andros Townsend can get in (the England team) then it opens it up to anybody.' Paul Merson had another dig at Andros Townsend after his appearance for Tottenham against Burnley . Townsend was brought on in the 83rd minute for Tottenham as they drew 0-0 against Burnley . Andros Townsend scores England's equaliser in their 1-1 friendly draw with Italy in Turin on Tuesday night . The former Arsenal man was proven wrong when Townsend hit a stunning equaliser for England against Italy and he duly admitted his mistake. 'It's not as though I was watching hoping he wouldn't score for England, I'm genuinely pleased for him and fair play to him – it was a great goal,' Merson said. 'It's just a matter of opinion, and my opinion was that he got pulled off after half an hour at Manchester United in front of Roy Hodgson, so he shouldn't have been in the squad. 'When I'm wrong, I hold my hands up. I don't have a problem with doing that - I'll always be the first to admit when I'm wrong.' Townsend hit back at Merson on Twitter after scoring for England against Italy . Sky Sports pundit  Merson (centre) criticised Townsend's call-up to the England squad last week . Townsend hit back at Merson after netting for England in Turin on Wednesday, saying 'Not bad for a player that should be 'nowhere near the squad' ay @PaulMerse?' Any bad feeling between the pair seemed to have passed but Merson was unable to resist having another dig at Townsend after Tottenham drew at Turf Moor.
Summary:
paul merson has restarted his row with andros townsend after the tottenham midfielder was brought on with only seven minutes remaining in his team 's 0-0 draw with burnley . townsend was brought on in the 83rd minute for tottenham as they drew 0-0 against burnley . paul merson had another dig at andros townsend after scoring for england against italy ."""

max_length = 200
response = get_chatgpt_response(model,input,max_length)
c = 4