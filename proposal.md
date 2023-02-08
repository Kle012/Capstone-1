### STEP ONE: INITIAL PROJECT IDEAS

- **IDEA 1**: Weebs Page
    > API: https://kitsu.docs.apiary.io/#?ref=apilist.fun
    Focus on: list all anime in the database, show an anime based on search, users will be able to create an account and create a favorites list

- **IDEA 2**: Recipes Page
    > API: https://spoonacular.com/food-api 
    Focus on: Users will be able to create an account and bookmark any recipes, users will be able to search for recipes by ingredients, get similar recipes, and get random recipes

- **IDEA 3**: Lyrics Page
    > API: https://developer.musixmatch.com/documentation?ref=apilist.fun
    Focus on: Users will be able to create an account and bookmark any lyrics, users will be able to get a track/an artist/album from the database, able to display the lyrics of a given track.



### STEP TWO: PROJECT PROPOSAL
- What goal will your website be designed to achieve?
    > An application where users can sign up, log in, searh, watch, and bookmark anime. User can also create, like, and comment on post.

- What kind of users will visit your site? In other words, what is the demographic of your users?
    > Anime fans, from kids to young and middle age adults.

- What data do you plan on using? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.
    > Users data, anime list and categories data, Post data, Comment data

- In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:
  > What does your database schema look like?
  > - Users: id, first name, last name, username, password, email, anime id
  > - Anime: id, title, episode count, average rating
  > - Post: id, user id, created at, anime id
  > - Comment: id, user id, created at, post id 

  > What kinds of issues might you run into with your API?
  > - Users might not find the anime they were looking for, unable to post or comment, or unable to bookmark anime

  > Is there any sensitive information you need to secure?
  > - Client secret for authentication
  > - Access token
  > - User's password

  > What functionality will your app include?
  > - Search, bookmark, post, comment

  > What will the user flow look like?
  > - The user will sign up then they will be taken to an anime list, from here, user can click on any anime to watch, bookmark if they like it, leave a post reagarding this anime and leave comments. User also be able to log out and log back in to continue watching or comments.

  > What features make your site more than CRUD? Do you have any stretch goals?
  > - Send an email welcome user when they sign up 



























