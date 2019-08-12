library(cowplot)
library("ggplot2")
library("zoom")
library("stats")
library(plyr)
library("dplyr")
library("colorspace")
library("RColorBrewer")
library(purrr)
library(zoo)
library(EnvStats)
library(grid)
library(plotly)
###################
# Load data       #
###################

dqn_path = '~/Projects/atari/vgdl/vgdl/dqn_interaction_data/interaction_data'
# dates = list('local', 'mar1') #feb27 has some games
# mar6: random policy but with 15 losses per level limit
# dates = list('mar1', 'mar9', 'mar23') ## old EMPA runs. not 10x.
# mar28: EMPA 10x
# apr4: e-greedy 10x, random policy 10x but incomplete.
dates = list('mar28', 'apr4')
## everything starting mar23 has no 15-loss cutoff.
groups = list.files('~/Projects/atari/vgdl/vgdl/human_interaction_data')
dqn_files = list.files(dqn_path)

olddqninteractiondata = filter(interactiondata, short_agent_type=='DDQN')
old_sum_dataframes = sum_dataframes

### Toggle the below line to alter what you're reading in
data_to_load = 'EMPA'
data_to_load = 'human'
data_to_load = 'DDQN'
  
if (data_to_load == 'EMPA'){
  dates_or_groups = dates
}else if (data_to_load == 'human'){
  dates_or_groups = groups
}else if (data_to_load == 'DDQN'){
  dates_or_groups = dqn_files
}


## load data
dates_or_groups_100k=c()
for (d in dates_or_groups){
  if (grepl('100k', d) & grepl('seed0', d)){
    dates_or_groups_100k = c(dates_or_groups_100k, d)
  }
}
data = load_data(data_to_load, dates_or_groups_100k) #takes a while
#interactiondata = rbind(humaninteractiondata, empa_interactiondata, dqninteractiondata) ## legacy, in case you need to load old data again.
#interactiondata = select(interactiondata, names(data))
# interactiondata = filter(interactiondata, short_agent_type!='human')

dqn_with_valence = add_valence_to_data(data)
dqn_sum_dataframes = make_sum_dataframes(dqn_with_valence)

## now bind to existing data
interactiondata = rbind(interactiondata, data)
## add hand-coded valence
data_with_valence = add_valence_to_data(interactiondata)
## calculate with within-agent normalized valence info
sum_dataframes = make_sum_dataframes(data_with_valence)



### temporary script for adding subject IDs:
# levels(interactiondata$subject_ID) = c(levels(interactiondata$subject_ID), 'DDQN 100k', 'DDQN 10k', 'DDQN 1k')
# interactiondata[interactiondata$short_agent_type=='DDQN 100k',]$subject_ID = 'DDQN 100k'
# interactiondata[interactiondata$short_agent_type=='DDQN 10k',]$subject_ID = 'DDQN 10k'
# interactiondata[interactiondata$short_agent_type=='DDQN 1k',]$subject_ID = 'DDQN 1k'
# 
# 
# levels(data_with_valence$subject_ID) = c(levels(data_with_valence$subject_ID), 'DDQN 100k', 'DDQN 10k', 'DDQN 1k')
# data_with_valence[data_with_valence$short_agent_type=='DDQN 100k',]$subject_ID = 'DDQN 100k'
# data_with_valence[data_with_valence$short_agent_type=='DDQN 10k',]$subject_ID = 'DDQN 10k'
# data_with_valence[data_with_valence$short_agent_type=='DDQN 1k',]$subject_ID = 'DDQN 1k'


# colors=c('grey50', 'steelblue3', 'palegreen3', 'slateblue1', 'slateblue2', 'indianred3')
# names(colors) = c('DDQN', 'EMPA', 'human', 'e-greedy .05', 'e-greedy .1', 'random policy')

interactioncolors = c('steelblue1',
           'purple2', #'mediumorchid2',
           'firebrick2',# 'seagreen3','darkolivegreen1',
           'palegreen3',# 'tomato2', 'salmon', 
           'gray50', 'gray52', 'gray54',
           'gray50', 'gray52', 'gray54')
# 'darkslategray3', 'darkslategray2', 'darkslategray1')#, 'mediumpurple2', 'aquamarine3', 'coral3')
names(interactioncolors)=c('EMPA', 'e-greedy', 'random', 'human', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k', 'DDQN', 'DDQN', 'DDQN')



### important
corr_dataframe = data.frame(short_agent_type=as.character(), game_name=as.character(), positive=as.numeric(), instrumental=as.numeric(), neutral=as.numeric(), negative=as.numeric())
for (game in unique(sum_dataframes$game_name)){
  game_data = filter(sum_dataframes, game_name==game)
  for (agent in c('EMPA', 'human', 'e-greedy .1', 'random policy', 'DDQN 100k')){
    a=filter(game_data, short_agent_type==agent)
    if (length(a$short_agent_type)>0){
      row = data.frame(short_agent_type=agent, game_name=game, positive=unique(a[a$valence=='positive',]$across_level_normalized_count),
                       instrumental=unique(a[a$valence=='instrumental',]$across_level_normalized_count),
                       neutral=unique(a[a$valence=='neutral',]$across_level_normalized_count),
                       negative=unique(a[a$valence=='negative',]$across_level_normalized_count))
      corr_dataframe=rbind(corr_dataframe, row)      
    }

  }
}

## important: turn corr_dataframe into different format
unpacked_corr_dataframe = data.frame(short_agent_type = as.character(), game_name=as.character(), valence = as.character(), mean_count=as.numeric())
for (agent in unique(corr_dataframe$short_agent_type)){
  for (game in unique(corr_dataframe$game_name)){
    dat = filter(corr_dataframe, short_agent_type==agent, game_name==game)
    if (length(dat$short_agent_type)>0){
      for (val in c('positive', 'instrumental', 'neutral', 'negative')){
        row = data.frame(short_agent_type=agent, game_name=game, valence=val, mean_count = dat[,c(val)])
        unpacked_corr_dataframe = rbind(unpacked_corr_dataframe, row)
      }
    }
  }
}
normalized_per_agent_counts = unpacked_corr_dataframe
normalized_per_agent_counts = filter(normalized_per_agent_counts, !(game_name%in%excluded_games))
## DON"T RUN THIS COMMAND ONCE YOU've PROCESSED BOULDERDASH
# normalized_per_agent_counts = filter(normalized_per_agent_counts, !grepl('boulderdash', game_name))


## Raw counts of interactions (used for plotting)
## WARNING: This is slow
raw_count_df=data.frame(short_agent_type=as.character(), subject_ID=as.character(), game_name=as.character(), valence=as.character(), raw_count=as.numeric())
# tmp_dwv = filter(data_with_valence, short_agent_type%in%c('DDQN 100k', 'DDQN 10k', 'DDQN 1k'))
for (game in unique(data_with_valence$game_name)){
  print (game)
  game_data = filter(data_with_valence, game_name==game)
  for (subject in unique(game_data$subject_ID)){
    print (subject)
    subject_data = filter(game_data, subject_ID==subject, grepl('avatar', event_type))
    for (each_valence in unique(data_with_valence$valence)){
      if (!is.na(each_valence)){
        row = data.frame(short_agent_type=subject_data$short_agent_type[1], subject_ID=subject, game_name=game, valence=each_valence, raw_count=sum(filter(subject_data, valence==each_valence)$count))
        raw_count_df = rbind(raw_count_df, row)
      }
      
    }
  }
}

## Per-subject means (used to compute squared distances)
mean_raw_count_df=data.frame(short_agent_type=as.character(), subject_ID=as.character(), game_name=as.character(), valence=as.character(), mean_count=as.numeric())
for (game in unique(raw_count_df$game_name)){
  for (agent in unique(raw_count_df$short_agent_type)){
    for (each_valence in unique(raw_count_df$valence)){
      row = data.frame(short_agent_type=agent, game_name=game, valence=each_valence, mean_count=mean(filter(raw_count_df, game_name==game, short_agent_type==agent, valence==each_valence)$raw_count))
      mean_raw_count_df = rbind(mean_raw_count_df, row)
    }
  }
}
mean_raw_count_df = filter(mean_raw_count_df, !(game_name%in%excluded_games))

create_distance_dataframe = function(count_df, metric, constant){
  ## count_df: mean_raw_count_df: mean per-subject counts  or normalized_per_agent_counts
  ## constant is only used for cross-entropy loss
  ## Choices for metric: 'cosine', 'avg_absolute_difference', 'avg_squared_difference', 'cross-entropy'
  
  ### Calculate squared differences of absolute model counts:
  human_empa=c()
  human_random=c()
  human_e_greedy=c()
  human_ddqn=c()
  
  ## Calculate distance between models in absolute counts
  for (game in unique(count_df$game_name)){
    game_data = filter(count_df, game_name==game)
    human_empa = c(human_empa,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                   c(filter(game_data, short_agent_type=='EMPA', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='EMPA', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='EMPA', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='EMPA', valence=='negative')$mean_count),
                                                   metric, constant))
    human_random = c(human_random,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                         filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                         filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                         filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                       c(filter(game_data, short_agent_type=='random policy', valence=='positive')$mean_count, 
                                                         filter(game_data, short_agent_type=='random policy', valence=='instrumental')$mean_count,
                                                         filter(game_data, short_agent_type=='random policy', valence=='neutral')$mean_count,
                                                         filter(game_data, short_agent_type=='random policy', valence=='negative')$mean_count),
                                                       metric, constant))
    human_e_greedy = c(human_e_greedy,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                             filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                             filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                             filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                           c(filter(game_data, short_agent_type=='e-greedy .1', valence=='positive')$mean_count, 
                                                             filter(game_data, short_agent_type=='e-greedy .1', valence=='instrumental')$mean_count,
                                                             filter(game_data, short_agent_type=='e-greedy .1', valence=='neutral')$mean_count,
                                                             filter(game_data, short_agent_type=='e-greedy .1', valence=='negative')$mean_count),
                                                           metric, constant))
    human_ddqn = c(human_ddqn,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                   c(filter(game_data, short_agent_type=='DDQN 100k', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='DDQN 100k', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='DDQN 100k', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='DDQN 100k', valence=='negative')$mean_count),
                                                   metric, constant))
  }
  corr_frame_vert_absolute = data.frame(rbind(
    cbind(as.character(unique(count_df$game_name)), 'human_empa', human_empa),
    cbind(as.character(unique(count_df$game_name)), 'human_e_greedy', human_e_greedy),
    cbind(as.character(unique(count_df$game_name)), 'human_random', human_random),
    cbind(as.character(unique(count_df$game_name)), 'human_ddqn', human_ddqn)))
  names(corr_frame_vert_absolute) = c('game_name', 'type', 'distance')
  
  if (missing(constant)){
    constant = ''
  }
  corr_frame_vert_absolute$metric = paste(metric, as.character(constant), sep=' ')
  return(corr_frame_vert_absolute)
}

# cross_entropy_01 = create_distance_dataframe(mean_raw_count_df, 'cross-entropy',.1)
# cross_entropy_1 = create_distance_dataframe(mean_raw_count_df,'cross-entropy',1)
# abs_distance = create_distance_dataframe(mean_raw_count_df,'avg_absolute_difference')
# sq_distance = create_distance_dataframe(mean_raw_count_df,'avg_squared_difference')
# all_distances_absolute_counts = rbind(cross_entropy_01, cross_entropy_1, abs_distance, sq_distance)


# normalized_cross_entropy_01 = create_distance_dataframe(normalized_per_agent_counts, 'cross-entropy',.1)
# normalized_cross_entropy_1 = create_distance_dataframe(normalized_per_agent_counts,'cross-entropy',1)
normalized_abs_distance = create_distance_dataframe(normalized_per_agent_counts,'avg_absolute_difference')
# normalized_sq_distance = create_distance_dataframe(normalized_per_agent_counts,'avg_squared_difference')
# all_distances_normalized_counts = rbind(normalized_cross_entropy_01,normalized_cross_entropy_1,normalized_abs_distance,normalized_sq_distance)

## to see actual scores given by each metric for some game:
filter(all_distances, game_name%in%c('chase'))

normalized_abs_distance_best_models = find_best_model(normalized_abs_distance)
## top 4: ee_2, chase_1, chase, chase_3, missilecommand_2
abs_distance_best_models = find_best_model(abs_distance)
## top 4: sokoban_1, chase, push_boulders_1, relational_2
cross_entropy_best_models = find_best_model(cross_entropy_01)
## top 4: chase, ee_2, chase_1, antagonist_1

empa_best = filter(normalized_abs_distance_best_models, type=='human_empa')
empa_best[order(empa_best$margin),]
ee_best[order(ee_best$margin),]
ddqn_best[order(ddqn_best$margin),]

p = ggplot(filter(normalized_abs_distance_best_models, type!='human_random'), aes(x=as.numeric(as.character(margin)), fill=as.factor(type), color=as.factor(type)))
p=p+geom_density(alpha=.4)+xlab('distance')+ggtitle('Distribution of margins (best_model - second_best)')#+xlim(0,100000)
p

margin_cutoff = 0.02
calculate_proportions = function(best_model_df, margin_cutoff){
  proportion_df = data.frame(type=as.character(), normalized_count=as.numeric(), metric=as.character())
  z=length(filter(normalized_abs_distance_best_models, margin>margin_cutoff)$margin)
  for (model in unique(best_model_df$type)){
    proportion = sum(filter(normalized_abs_distance_best_models, margin>margin_cutoff)$type==model)/z
    row = data.frame(type=model, normalized_count=proportion, metric=best_model_df$metric[1])
    proportion_df = rbind(proportion_df, row)
  }

  return(proportion_df)
}
normalized_abs_distance_best_models_with_cutoff = calculate_proportions(filter(normalized_abs_distance_best_models, type!='human_random'), margin_cutoff)

normalized_abs_distance$distance=as.numeric(as.character(normalized_abs_distance$distance))


## return here
p = ggplot(filter(normalized_abs_distance, type%in%c('human_empa', 'human_ddqn')), aes(x=distance, fill=type, color=type))+geom_density(alpha=.4)
p

normalized_abs_distance_new_names=filter(normalized_abs_distance, type%in%c('human_empa', 'human_ddqn'))

normalized_abs_distance_new_names[normalized_abs_distance_new_names$type=='human_empa',]$type=as.factor('EMPA')

unique(normalized_abs_distance$game_name)
static_games = c('push_boulders_2', 'push_boulders', 'push_boulders_1', 'preconditions', 'preconditions_1', 'preconditions_2', 'bait', 'bait_1', 'bait_2', 
                 'watergame', 'watergame_1', 'watergame_2', 'relational', 'sokoban', 'sokoban_1', 'sokoban_2', 'ee')


saved_normalized_abs_distance = normalized_abs_distance
normalized_abs_distance$game_type = NA
normalized_abs_distance$formatted_type = NA
for (i in 1:length(normalized_abs_distance$game_name)){
  if (normalized_abs_distance$type[i]=='human_empa'){
    normalized_abs_distance$formatted_type[i]='EMPA'
  }
  if (normalized_abs_distance$type[i]=='human_ddqn'){
    normalized_abs_distance$formatted_type[i]='DDQN'
  }
  if (normalized_abs_distance$game_name[i]%in%static_games){
    normalized_abs_distance$game_type[i]='Slow-paced games'
  }
  else{
    normalized_abs_distance$game_type[i]='Fast-paced games'
    
  }
}


## new supplementary figure
p = ggplot(filter(normalized_abs_distance, type%in%c('human_empa', 'human_ddqn')), aes(x=formatted_type,y=distance, fill=type, fill=type))+
  geom_boxplot()+scale_fill_manual(values=c('grey50', 'steelblue1'))+scale_color_manual(values=c('grey50', 'steelblue1'))+coord_flip()+
  facet_wrap(~game_type, nrow=2)+
  theme(plot.title=element_text(family='',face='plain', size=26),axis.text.x=element_text(size=22),
        axis.text.y=element_text(size=22),axis.title.x=element_text(size=24),axis.title.y=element_text(size=24), strip.text.x=element_text(size=22), legend.position='none')+
  theme(strip.text.x = element_text(margin = margin(.2,0,.2,0, "cm")))+
  ylab("L1 distance between model and human interaction distributions")+xlab("Model type")+ylim(0,.5)
p


summary_abs_distance = summarySE(filter(normalized_abs_distance, type%in%c('human_empa', 'human_ddqn')), measurevar='distance', groupvars=c('formatted_type','game_type'))

pd = position_dodge(width=0.5)
ggplot(summary_abs_distance, aes(x=formatted_type, y=distance, colour=formatted_type, width=.2)) + scale_color_manual(values=c('grey50', 'steelblue1'))+
  geom_errorbar(aes(ymin=distance-ci, ymax=distance+ci), width=.5, position=position_dodge(-1),size=2) +
  geom_line(position=pd) +
  geom_point(position=pd,size=5,shape=18) + theme(plot.title=element_text(family='',face='plain', size=24),axis.text.x=element_text(size=20),
                                                             axis.text.y=element_text(size=20),axis.title.x=element_text(size=22),axis.title.y=element_text(size=22), strip.text.x=element_text(size=22), legend.position='none')+
  theme(strip.text.x = element_text(margin = margin(.15,0,.15,0, "cm")))+
  ylab("L1 distance between model and human interaction distributions")+xlab("Model type")+ylim(0,.4)+ theme(aspect.ratio = 1/8)+
  facet_wrap(~game_type, nrow=2)+
  coord_flip()


          t.test(filter(normalized_abs_distance, type%in%c('human_empa'), game_type=='Static games')$distance, filter(normalized_abs_distance, type%in%c('human_ddqn'), game_type=='Static games')$distance)
t.test(filter(normalized_abs_distance, type%in%c('human_empa'), game_type=='Dynamic games')$distance, filter(normalized_abs_distance, type%in%c('human_ddqn'), game_type=='Dynamic games')$distance)


t.test(filter(normalized_abs_distance, type%in%c('human_empa'), game_type=='Static games')$distance)


one_d = data.frame(game_name=filter(normalized_abs_distance, type=='human_empa')$game_name, distance=distance_to_empa/(distance_to_ddqn+distance_to_empa))
p = ggplot(one_d, aes(x=distance))+geom_density(adjust=1/4, color='palegreen3', fill='palegreen3')
p


### convert to format for ternary plot
games_used_in_12_plot = c(group1, group2)
max_distance = max(as.numeric(as.character(normalized_abs_distance$distance)))
human_empa = max_distance-as.numeric(as.character(filter(normalized_abs_distance, type=='human_empa')$distance))
human_e_greedy = max_distance-as.numeric(as.character(filter(normalized_abs_distance, type=='human_e_greedy')$distance))
human_ddqn = max_distance-as.numeric(as.character(filter(normalized_abs_distance, type=='human_ddqn')$distance))
game_names = filter(normalized_abs_distance, type=='human_empa')$game_name
df = data.frame(game_names, human_empa, human_e_greedy, human_ddqn)
df$best_model=NA
df$used_in_12_plot=5
for (i in 1:length(df$game_names)){
  df$best_model[i] = c('human_empa', 'human_e_greedy', 'human_ddqn')[which(df[i,2:4]==max(df[i,2:4]))]
  if (df$game_names[i]%in%games_used_in_12_plot){
    df$used_in_12_plot[i] = 10
  }
}


## Simplex plot
## see here for a nice example: https://xang1234.github.io/ternary/
axis <- function(title) {
  list(
    title = title,
    titlefont = list(
      size = 20
    ),
    tickfont = list(
      size = 20
    ),
    tickcolor = 'rgba(0,0,0,0.5)',
    ticklen = 5,
    showgrid = FALSE
  )
}

similarity_colors = c('steelblue1', 'slateblue1', 'gray50')
names(similarity_colors) = c('human_empa', 'human_e_greedy', 'human_ddqn')

p <- df %>% 
  plot_ly() %>%
  add_trace(
    type = 'scatterternary',
    mode = 'markers',
    a = ~human_empa,
    b = ~human_e_greedy,
    c = ~human_ddqn,
    color = ~best_model,colors=~similarity_colors,
    # size = ~used_in_12_plot,
    text = ~game_names,
    marker = list( 
      # symbol = 100,
      # color = '#DB7365',
      symbol='circle',
      # alpha=.7,
      size = 14,
      # sizemode='diameter',
      # sizeref=10,
      line = list('width' = 1)
    )
  ) %>% 
  layout(
    # title = "Simple Ternary Plot with Markers",
    ternary = list(
      # sum = 100,
      aaxis = axis('EMPA'),
      baxis = axis('e-greedy EMPA'),
      caxis = axis('DDQN')
    )
  )

p


##empa best (hybrid sorting by margin and also coverage and game name variety): 'ee_3', 'relational','preconditions', 'sokoban', 'zelda', 'butterflies_1', 'bait_2'
## ee best: 'chase', 'missilecommand_2', 'antagonist_2', (or antagonist_1), 'portals_1'
## ddqn best: 'missilecommand_3', 'closing_gates_1', 

## sokoban, relational, push_boulders all pretty similar for humans

## why is distance 0 in some games, like helper?
## you can't fiter by the one that has the best model, or you'll have ties and will add too many rows.

## figure out why ddqn used to show up in abs_distance. it actually just couldn't have. distance should have been too big.

## distribution of squared distances per model
# p = ggplot(corr_frame_vert_absolute_1, aes(x=as.numeric(as.character(distance)), fill=as.factor(type), color=as.factor(type)))
# p=p+geom_density(alpha=.4)+xlab('distance')+ggtitle('Distribution of cross-entropies')#+xlim(0,100000)
# p

absolute_counts_no_random = calculate_proportion_of_games_best_fit_by_each_model(filter(abs_distance, type%in%c('human_empa', 'human_e_greedy', 'human_ddqn')))
absolute_counts = calculate_proportion_of_games_best_fit_by_each_model(abs_distance)

normalized_absolute_counts_no_random = calculate_proportion_of_games_best_fit_by_each_model(filter(normalized_abs_distance, type%in%c('human_empa', 'human_e_greedy', 'human_ddqn')))

# metric_df = normalized_absolute_counts_no_random

metric_df = normalized_abs_distance_best_models_with_cutoff
p = ggplot(transform(metric_df, type=factor(type, levels=c('human_empa','human_e_greedy', 'human_ddqn'))), aes(x=type, y=normalized_count))
p = p+geom_bar(stat='identity')+scale_x_discrete(breaks=c('human_empa','human_e_greedy', 'human_ddqn'),
                                                 labels=c("EMPA", "e-greedy", 'DDQN 100k'), drop=FALSE)+
  ylab('Proportion')+xlab('Model')+ggtitle(paste('Proportion of games best fit by model type. Metric:', metric_df$metric[1], sep=' '))+ylim(0,.8)
p

p = ggplot(transform(metric_df, type=factor(type, levels=c('human_empa','human_e_greedy','human_random', 'human_ddqn'))), aes(x=type, y=normalized_count))
p = p+geom_bar(stat='identity')+scale_x_discrete(breaks=c('human_empa','human_e_greedy','human_random', 'human_ddqn'),
                                                 labels=c("EMPA", "e-greedy", "random policy", 'DDQN 100k'), drop=FALSE)+
  ylab('Proportion')+xlab('Model')+ggtitle(paste('Proportion of games best fit by model type. Metric:', metric_df$metric[1], sep=' '))+ylim(0,.7)
p
#8,10

## split figure of 12 interaction valence plots into 7,3,2, which roughly corresponds to the normalized counts.
filter(corr_frame, nearest_to_human=='human_empa')
filter(corr_frame, nearest_to_human=='human_e_greedy')
filter(corr_frame, nearest_to_human=='human_random')

mean(human_empa, na.rm=TRUE)
mean(human_random, na.rm=TRUE)
mean(human_e_greedy, na.rm=TRUE)

## unnormalized interactions across levels, for each game
tickmarks = c(10,100,1000,10000,100000,1000000,10000000)
logtickmarks=c(.05,log(tickmarks,10))
tickmarks = c(1,tickmarks)
for (game in unique(raw_count_df$game_name)){
  ## add random policy again
  df = transform(filter(raw_count_df, game_name==game), short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k')),
            valence=factor(valence, levels=c('positive', 'instrumental', 'neutral', 'negative')))
  
  p = ggplot(filter(df, !is.na(short_agent_type)),
             aes(x=valence, y=log(raw_count,10)+.05, fill=short_agent_type))+facet_wrap(~short_agent_type, ncol=1, drop=TRUE)
  p=p+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
    scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (unnormalized)')+
    scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,log(1000000,10)))+ggtitle(game)+theme(axis.text.x = element_text(angle = 90, hjust = 1))
  p
  newdir='~/Projects/atari/vgdl/interaction_plots/by_valence_all_levels_unnormalized/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=5, height=8)
}


## just transform to log in the dataframe and then plot normally.
df$log_raw_count = log(df$raw_count,10)+.05

## determine groups first. once you have them you can do this.
group1 = c('bait', 'bees_and_birds', 'corridor', 'ee_3', 'frogs', 'sokoban')
group2 = c('zelda', 'butterflies', 'chase', 'antagonist_1', 'portals_1', 'closing_gates')
df = transform(filter(raw_count_df, game_name%in%group1), short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k')),
               valence=factor(valence, levels=c('positive', 'instrumental', 'neutral', 'negative')))
df$log_raw_count = log(df$raw_count,10)+.05
p = ggplot(filter(df, !is.na(short_agent_type)),
           aes(x=valence, y=log_raw_count, fill=short_agent_type))+facet_grid(short_agent_type ~ game_name, scales='free')

                      # aes(x=valence, y=log_raw_count, fill=short_agent_type))+facet_grid(short_agent_type ~ game_name, scales='free',space='free')
p=p+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
  scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (unnormalized)')+
  scale_y_continuous(breaks=logtickmarks, labels=tickmarks)+theme(panel.spacing.x = unit(2, "lines"))+theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  theme(panel.background = element_rect(fill = "gray95",
                                  colour = "gray95",
                                  size = 0.5, linetype = "solid"))
p
##6x18

## determine groups first. once you have them you can do this.
group1 = c('ee_3', 'frogs', 'corridor', 'bait', 'bees_and_birds','sokoban')
group2 = c('antagonist_1', 'zelda', 'chase',  'butterflies','closing_gates', 'portals_1' )
df = transform(filter(raw_count_df, game_name%in%group1), short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k')),
               valence=factor(valence, levels=c('positive', 'instrumental', 'neutral', 'negative')))
df = transform(df, game_name=factor(game_name, levels=group1))

# df$log_raw_count = log(df$raw_count,10)+.05
p = ggplot(filter(df, !is.na(short_agent_type), !is.na(game_name)),
           aes(x=valence, y=raw_count, fill=short_agent_type))+facet_grid(short_agent_type ~ game_name, scales='free')

# aes(x=valence, y=log_raw_count, fill=short_agent_type))+facet_grid(short_agent_type ~ game_name, scales='free',space='free')
p=p+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
  scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (unnormalized)')+
  theme(panel.spacing.x = unit(2, "lines"))+theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  theme(panel.background = element_rect(fill = "gray95",
                                        colour = "gray95",
                                        size = 0.5, linetype = "solid"))
p
##6x18



## ddqn should be best on these: (it is; the plots correspond to what the numbers predict)
group3 = c('closing_gates_1', 'lemmings_1', 'missilecommand_3', 'sokoban_1', 'surprise_1')

normalized_per_agent_counts


###
### For generating the actual figure for normalized interaction counts.
## determine groups first. once you have them you can do this.
# group1 = c('bait', 'bees_and_birds', 'corridor', 'ee_3', 'frogs', 'sokoban')
# group2 = c('zelda', 'butterflies', 'chase', 'antagonist_1', 'portals_1', 'closing_gates')
group1 = c('ee_3', 'frogs', 'corridor', 'bait', 'bees_and_birds','sokoban')
group2 = c('antagonist_1', 'zelda', 'butterflies','closing_gates', 'portals_1','chase')
# df = transform(filter(normalized_per_agent_counts, game_name%in%group2), short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k')),
#                valence=factor(valence, levels=c('positive', 'instrumental', 'neutral', 'negative')))
# df = transform(df, game_name=factor(game_name, levels=group2))
# p = ggplot(filter(df, !is.na(short_agent_type), !is.na(game_name)),
#            aes(x=valence, y=mean_count, fill=short_agent_type))+facet_grid(short_agent_type ~ game_name, scales='free')
# p=p+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
#   scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (normalized)')+
#   theme(panel.spacing.x = unit(2, "lines"))+theme(axis.text.x = element_text(angle = 90, hjust = 1))+
#   theme(panel.background = element_rect(fill = "gray95",
#                                         colour = "gray95",
#                                         size = 0.5, linetype = "solid"))
# p
## 6x18

## interactions by valence, across levels (relative )
## figure 6A
for (game in unique(sum_dataframes$game_name)){
  # for (game in c('ee_3', 'frogs', 'corridor', 'bait', 'bees_and_birds', 'sokoban', 'antagonist', 'zelda', 'butterflies', 'closing_gates', 'portals_1', 'chase')){
    
    if (!(game %in% excluded_games)){
    
    # distances = filter(corr_frame, game_name==game)
    distances = filter(corr_frame_vert_absolute, game_name==game)
    h_e = filter(distances, type=='human_empa')
    h_eg = filter(distances, type=='human_e_greedy')
    h_r = filter(distances, type=='human_random')
    
    # relevant_distances = paste('\n',metric,'\nhuman-empa:', distances$human_empa, '\nhuman-e-greedy:', distances$human_e_greedy, '\nhuman-random:', distances$human_random, sep=' ')
    relevant_distances = c()
    game_title=gsub('_',' ',game)
    # relevant_distances = paste('\n',metric,'\nhuman-empa:', h_e$distance, '\nhuman-e-greedy:', h_eg$distance, '\nhuman-random:', h_r$distance, sep=' ')
    
    data_subset = filter(sum_dataframes, game_name==game)
    ## renaming model here
    levels(data_subset$short_agent_type) = c('human', 'DDQN', 'EMPA', 'e-greedy', 'random policy', 'DDQN')
    # df = transform(data_subset, short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy', 'DDQN')))
    df = transform(data_subset, short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'DDQN')))
    
    p = ggplot(filter(df, !is.na(short_agent_type)), aes(x=valence, y=across_level_normalized_count, fill=short_agent_type))
    p=p+geom_bar(stat='identity', position='dodge')+ggtitle(paste(game_title, relevant_distances, sep=''))+
      facet_wrap(~short_agent_type, ncol=1, strip.position='bottom')+ylim(0,1)+
      scale_fill_manual(name="short_agent_type", values=interactioncolors)+ xlab('Interaction valence')+ylab('Interaction count (normalized)')+
      theme(axis.text.x = element_text(angle = 90, hjust = 1, size=22),axis.text.y=element_text(size=22),
            axis.title.x=element_text(size=20),axis.title.y=element_text(size=24),plot.title=element_text(size=26),legend.position='none')
     p
    newdir='~/Projects/atari/vgdl/interaction_plots/by_valence_all_levels_large_text_no_DQN/'
    dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
    title = paste(newdir, game, '.png', sep='')
    ggsave(title, plot=p, width=4, height=8)
    # ggsave(title, plot=p, width=5, height=9)  
    
  }
}


# ## interactions by valence by level
# for (game in unique(sum_dataframes$game_name)){
#   if (!(game %in% c('jaws', 'jaws_1', 'jaws_2', 'missilecommand', 'missilecommand_1', 'missilecommand_4', 'helper', 'helper_1', 'helper_2'))){
#     
#     # game_data = filter(sum_dataframes, game_name==game, grepl('avatar', event_type), short_agent_type!='e-greedy')
#     game_data = transform(filter(sum_dataframes, game_name==game, grepl('avatar', event_type)), short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .05', 'DDQN', 'random policy')))
#     
#         game_data = select(game_data, short_agent_type, game_name, level, valence, per_level_normalized_count)
#     game_data = rbind(game_data, cbind(expand.grid(short_agent_type=unique(game_data$short_agent_type), game_name=unique(game_data$game_name),
#                                                                                    level=unique(game_data$level), valence=unique(game_data$valence)), 
#                                                 per_level_normalized_count=NA))
#     
#     
#   p = ggplot(game_data, aes(x=valence, y=per_level_normalized_count, fill=short_agent_type))
#     p=p+geom_bar(stat='identity', position='dodge')+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ggtitle(game)+facet_wrap(~level, nrow=1)+
#       scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (normalized)')
#     newdir='~/Projects/atari/vgdl/interaction_plots/by_valence_by_level/'
#     dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#     title = paste(newdir, game, '.png', sep='')
#     ggsave(title, plot=p, width=15, height=3)  
#     }
# }

## Collisions with deadly objects.
game_df = data.frame(short_agent_type=as.character(), game_name=as.character(), count=as.numeric())
# for (game in c('ee_3', 'zelda', 'bait', 'portals_1', 'surprise_1')){
for (game in unique(data_with_valence$game_name)){
  game_data = filter(data_with_valence, game_name==game, valence=='negative', grepl('avatar', event_type))
  # min_level = min(game_data$level_number)
  for (subject in unique(game_data$subject_ID)){
    short_agent_type = filter(game_data, subject_ID==subject)$short_agent_type[1]
    subject_data = filter(game_data, subject_ID==subject)
    
        # subject_data = filter(game_data, subject_ID==subject, level_number==min_level)
    if (length(subject_data$count)==0){
      interaction_count = 0
    }else{
      interaction_count = sum(subject_data$count)
    }
    row = data.frame(short_agent_type=short_agent_type, game_name=game, count=interaction_count)
    game_df = rbind(game_df, row)
  }
}
game_df = filter(game_df, !is.na(short_agent_type))
game_df$log_count = log(game_df$count,10)+.05

all_level_game_df = game_df
#first_level_game_df = game_df

### we only have data for 59 games bc that's the number of games that have negative interactions that we coded for.
### Generate data frame for scatter plots and correlations
human_cols = filter(all_level_game_df, short_agent_type=='human', game_name!='ee_3')
human_cols = aggregate(log_count ~ short_agent_type + game_name, human_cols, mean)
human_cols = arrange(human_cols, as.character(game_name))
human_cols = select(human_cols, -short_agent_type)
names(human_cols)[2] = 'human_log_count'

log_scatter_plot_df = data.frame(game_name=as.character(), human_log_count=as.numeric(), short_agent_type=as.character(), model_count=as.numeric())

for (agent in c('EMPA', 'e-greedy .1', 'DDQN 100k')){
    agent_data = filter(all_level_game_df, short_agent_type==agent, game_name!='ee_3')
    agent_data = aggregate(log_count ~ short_agent_type + game_name, agent_data, mean)
    agent_data = arrange(agent_data, as.character(game_name))
    agent_data = select(agent_data, -game_name)
    names(agent_data)[2] = 'model_log_count'
    log_scatter_plot_df = rbind(log_scatter_plot_df,  cbind(human_cols, agent_data))
}
names(log_scatter_plot_df)[3] = 'agent_type'

## Scatter plot of negative interactions
tickmarks = c(10,100,1000,10000,1e5)
logtickmarks=c(.05,log(tickmarks,10))
tickmarks = c(1,tickmarks)
p = ggplot(log_scatter_plot_df, aes(x=human_log_count, y=model_log_count, color=agent_type))
p = p+geom_point()+xlim(0,3)+ylim(0,5)+geom_abline(intercept=0, slope=1)+geom_smooth(method = "lm")+scale_color_manual(name="agent_type", values=colors)+
  scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,5))+scale_x_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,3))+
  xlab('human interaction count')+ylab('model interaction count')
p

model_human_correlations_logs = data.frame(agent_type=as.character(), correlation=as.numeric())
for (agent in unique(log_scatter_plot_df$agent_type)){
  d=filter(log_scatter_plot_df, agent_type==agent)
  corr = cor(select(d, human_log_count, model_log_count), method='spearman')[2]
  model_human_correlations_logs = rbind(model_human_correlations_logs, data.frame(agent_type=agent, correlation=corr))
}


human_cols = filter(all_level_game_df, short_agent_type=='human', game_name!='ee_3')
human_cols = aggregate(count ~ short_agent_type + game_name, human_cols, mean)
human_cols = arrange(human_cols, as.character(game_name))
human_cols = select(human_cols, -short_agent_type)
names(human_cols)[2] = 'human_count'

scatter_plot_df = data.frame(game_name=as.character(), human_log_count=as.numeric(), short_agent_type=as.character(), model_count=as.numeric())

for (agent in c('EMPA', 'e-greedy .1', 'DDQN 100k')){
  agent_data = filter(all_level_game_df, short_agent_type==agent, game_name!='ee_3')
  agent_data = aggregate(count ~ short_agent_type + game_name, agent_data, mean)
  agent_data = arrange(agent_data, as.character(game_name))
  agent_data = select(agent_data, -game_name)
  names(agent_data)[2] = 'model_count'
  scatter_plot_df = rbind(scatter_plot_df,  cbind(human_cols, agent_data))
}
names(scatter_plot_df)[3] = 'agent_type'

## Scatter plot of negative interactions
plots = list()
for (i in 1:length(unique(scatter_plot_df$agent_type))){
  agent = unique(scatter_plot_df$agent_type)[i]
  p = ggplot(filter(scatter_plot_df, agent_type==agent), aes(x=human_count, y=model_count, color=agent_type))
  p = p+geom_point()+geom_abline(intercept=0, slope=1)+geom_smooth(method = "lm")+scale_color_manual(name="agent_type", values=colors)+
    xlab('human interaction count')+ylab('model interaction count')
  plots[[i]] = p
}
layout = matrix(c(1:3), ncol=3)
m = multiplot(plotlist = plots[1:3], layout=layout)

model_human_correlations = data.frame(agent_type=as.character(), correlation=as.numeric())
for (agent in unique(scatter_plot_df$agent_type)){
  d=filter(scatter_plot_df, agent_type==agent)
  corr = cor(select(d, human_count, model_count), method='pearson')[2]
  model_human_correlations = rbind(model_human_correlations, data.frame(agent_type=agent, correlation=corr))
}




# ## per-game negative collision count
# for (game in unique(game_df$game_name)){
# # for (game in c('bait', 'ee_3', 'zelda', 'portals_1')){
#   p = ggplot(filter(transform(game_df, short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .05', 'DDQN', 'random policy'))),!is.na(short_agent_type), game_name==game), 
#              aes(x=short_agent_type, y=log_count, fill=short_agent_type))
#   p = p+geom_bar(position='dodge',stat='summary', fun.y='mean')+scale_fill_manual(name="short_agent_type", values=colors)+xlab('Agent type')+ylab('Collision count')+
#   ggtitle(paste('Agent collisions with deadly objects in', game, sep=' '))
#   
#   tickmarks = c(10,100,1000,10000)
#   logtickmarks=c(.05,log(tickmarks,10))
#   tickmarks = c(1,tickmarks)
#   p=p+scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,log(10000,10)))
#   newdir='~/Projects/atari/vgdl/interaction_plots/deadly_collisions/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, game, '.png', sep='')
#   ggsave(title, plot=p, width=10, height=10)  
# }

tmp_game_subset = c('ee_3', 'frogs', 'push_boulders', 'aliens', 'zelda', 'bait', 'chase', 'bees_and_birds', 'portals', 'preconditions', 'portals_1', 'surprise_1')
## log scale per negative collision plot
## add random policy

all_level_game_df$formatted_game_name = NA
for (i in 1:length(all_level_game_df$game_name)){
  all_level_game_df$formatted_game_name[i] = gsub('_',' ',all_level_game_df$game_name[i])
}

dqn_games = unique(filter(all_level_game_df, short_agent_type=='DDQN 100k')$formatted_game_name)
dqn_games=dqn_games[order(as.character(dqn_games))]

data_to_plot = filter(transform(all_level_game_df, short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k'))), game_name%in%dqn_games)
# data_to_plot = transform(filter(data_to_plot, game_name%in%tmp_game_subset), game_name=factor(game_name, levels=tmp_game_subset))
data_to_plot = filter(data_to_plot, !is.na(short_agent_type))

data_to_plot$formatted_game_name = NA
for (i in 1:length(data_to_plot$game_name)){
  data_to_plot$formatted_game_name[i] = gsub('_',' ',data_to_plot$game_name[i])
}


# saved_data_to_plot = data_to_plot
# data_to_plot$game_type=NA
# for (i in 1:length(data_to_plot$game_name)){
#  if(data_to_plot$game_name[i]%in%static_games){
#    data_to_plot$game_type[i] = 'Static'
#  } 
#   else{
#     data_to_plot$game_type[i] = 'Dynamic'
#   }
# }
# ## Figure 6C
# tickmarks = c(10,100,1000,10000,1e5,1e6)
# logtickmarks=c(.05,log(tickmarks,10))
# tickmarks = c(1,tickmarks)
# levels(data_to_plot$short_agent_type) = c('human', 'EMPA', 'e-greedy', 'DDQN')
# p = ggplot(filter(data_to_plot, short_agent_type%in%c('human','EMPA','DDQN')),
#            aes(x=formatted_game_name, y=log(count,10)+.05, fill=short_agent_type))+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
#   # facet_wrap(~short_agent_type,ncol=1,strip.position='bottom',shrink=TRUE)+
# facet_grid(vars(short_agent_type), vars(game_type))+
#     scale_fill_manual(name="short_agent_type", values=interactioncolors)+
#   theme(axis.text.x = element_text(angle = 90, hjust = 1),
#         axis.text.y=element_text(size=22),
#         axis.title.y=element_text(size=24), axis.title.x=element_text(size=24), plot.title=element_text(size=26))+
#   scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,5.5))+scale_x_discrete(limits=dqn_games)+theme(legend.position="none")+
#   ## or try limits=c(0,4.5)
#   ylab('Interactions with deadly items')+xlab('Game name')#+ggtitle('Collisions with deadly objects')
# p


## Figure 6C
tickmarks = c(10,100,1000,10000,1e5,1e6)
logtickmarks=c(.05,log(tickmarks,10))
tickmarks = c(1,tickmarks)
levels(data_to_plot$short_agent_type) = c('human', 'EMPA', 'e-greedy', 'DDQN')
p = ggplot(filter(data_to_plot, short_agent_type%in%c('human','EMPA','DDQN')),
           aes(x=formatted_game_name, y=log(count,10)+.05, fill=short_agent_type))+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
  facet_wrap(~short_agent_type,ncol=1,strip.position='bottom',shrink=TRUE)+
  scale_fill_manual(name="short_agent_type", values=interactioncolors)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),
        axis.text.y=element_text(size=22),
        axis.title.y=element_text(size=24), axis.title.x=element_text(size=24), plot.title=element_text(size=26))+
  scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,5.5))+scale_x_discrete(limits=dqn_games)+theme(legend.position="none")+
## or try limits=c(0,4.5)
 ylab('Interactions with deadly items')+xlab('Game name')#+ggtitle('Collisions with deadly objects')
p
## save as 12x12

# 
# dqn_games = unique(filter(game_df, short_agent_type=='DDQN')$game_name)
# data_to_plot = filter(transform(game_df, short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .05', 'random policy', 'DDQN'))), game_name%in%dqn_games)
# tickmarks = c(10,100,1000,10000)
# logtickmarks=c(.05,log(tickmarks,10))
# tickmarks = c(1,tickmarks)
# p = ggplot(data_to_plot, 
#            aes(x=game_name, y=log(count,10)+.05, fill=short_agent_type))+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
#   facet_wrap(~short_agent_type,ncol=1,strip.position='bottom',shrink=TRUE, space='free_y')+
#   scale_fill_manual(name="short_agent_type", values=colors)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+
#   # scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,4.5))+   #limits=c(0,log(100000,10)
#   ylab('Interaction count')+xlab('game name')+ggtitle('First-level collisions with deadly object')
# p
# 
# dqn_games = unique(filter(game_df, short_agent_type=='DDQN')$game_name)
# data_to_plot = filter(transform(game_df, short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .05', 'random policy', 'DDQN'))), game_name%in%dqn_games)
# tickmarks = c(10,100,1000,10000)
# logtickmarks=c(.05,log(tickmarks,10))
# tickmarks = c(1,tickmarks)
# p = ggplot(data_to_plot, 
#            aes(x=game_name, y=log(count,10)+.05, fill=short_agent_type))+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
#   facet_grid(short_agent_type ~ ., space='free_y', scales='free_y')+
#   scale_fill_manual(name="short_agent_type", values=colors)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+
#   # scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,4.5))+   #limits=c(0,log(100000,10)
#   ylab('Interaction count')+xlab('game name')+ggtitle('First-level collisions with deadly object')
# p
# 



## aggregate means and then plot margin over mean for each model.
game_agent_means = data.frame(data_to_plot %>% group_by(short_agent_type,game_name) %>% summarize(mean_count=mean(count, na.rm=TRUE)))
# game_agent_means$margin_over_worst_model = NA

## plot log ratio of collisions. high bar = good.
game_agent_means_with_margins = data.frame(short_agent_type=as.character(), game_name=as.character(), mean_count = as.numeric(), margin_over_worst_model=as.numeric())
for (game in unique(game_agent_means$game_name)){
  models_for_this_game = filter(game_agent_means, game_name==game)
  models_for_this_game$margin_over_worst_model = NA
  worst_mean_count = max(models_for_this_game$mean_count)
  models_for_this_game$margin_over_worst_model = worst_mean_count/models_for_this_game$mean_count
  game_agent_means_with_margins = rbind(game_agent_means_with_margins, models_for_this_game)
  }
# game_agent_means_with_margins$margin_over_worst_model = game_agent_means_with_margins$margin_over_worst_model+10e-8 ## to avoid log issue


p = ggplot(game_agent_means_with_margins, 
           aes(x=game_name, y=log(margin_over_worst_model,10), fill=short_agent_type))+geom_histogram(stat='summary', fun.y='mean', position='dodge')+facet_wrap(~short_agent_type,ncol=1)+
  scale_fill_manual(name="short_agent_type", values=colors)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,log(10000,10)))+
  ylab('Multiplicative margin over worst model')+xlab('game name')
p

# p = ggplot(game_agent_means_with_margins, 
#            aes(x=game_name, y=margin_over_worst_model, fill=short_agent_type))+geom_histogram(stat='summary', fun.y='mean', position='dodge')+facet_wrap(~short_agent_type,ncol=1)+
#   scale_fill_manual(name="short_agent_type", values=colors)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+
#   # scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,log(10000,10)))+
#   ylab('Margin over worst model (in collisions)')+xlab('game name')
# p

## interactions by valence by level, omitting neutral ones, and only plotting games/levels
## where EMPA and humans both produced data.
for (game in unique(sum_dataframes$game_name)){
  human = filter(sum_dataframes, game_name==game, short_agent_type=='human')
  empa = filter(sum_dataframes, game_name==game, short_agent_type=='EMPA')
  if (length(human$per_level_normalized_count)==length(empa$per_level_normalized_count) & sum(human$per_level_normalized_count)>0 & sum(empa$per_level_normalized_count)>0 &
      (sum(filter(human, valence=='positive')$per_level_normalized_count>0) & sum(filter(human, valence=='negative')$per_level_normalized_count>0) ||
      (sum(filter(empa, valence=='positive')$per_level_normalized_count>0) & sum(filter(empa, valence=='negative')$per_level_normalized_count>0))) ){
    
  p = ggplot(filter(sum_dataframes, game_name==game, valence!='neutral'), aes(x=valence, y=per_level_no_neutral_normalized_count, fill=short_agent_type))
  p=p+geom_bar(stat='identity', position='dodge')+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ggtitle(game)+facet_wrap(~level, nrow=1)+
    scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (normalized)')
  newdir='~/Projects/atari/vgdl/interaction_plots/by_valence_by_level_no_neutral/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=15, height=3) 
  }
}

## interactions by valence by level and agent type (same as above, but grouped by agent type)
for (game in unique(sum_dataframes$game_name)){
  p = ggplot(filter(sum_dataframes, game_name==game), aes(x=valence, y=per_level_normalized_count, fill=short_agent_type))
  p=p+geom_bar(stat='identity', position='dodge')+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ggtitle(game)+facet_grid(level~short_agent_type)+
    scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (normalized)')
  
  newdir='~/Projects/atari/vgdl/interaction_plots/by_valence_by_agent_by_level/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=10, height=15)  
}


## the way to avoid having all the subject_IDs and generating combinations that include them is to calculate the means of each short_agent_type, level_number, event_type category

## interactions by event type
for (game in unique(data_with_valence$game_name)){
  
  # game_data = filter(data_with_valence, game_name==game, grepl('avatar', event_type), short_agent_type!='e-greedy')
  game_data = filter(data_with_valence, game_name==game, grepl('avatar', event_type))
  
    g=data.frame(game_data %>% group_by(game_name, level_number, event_type, short_agent_type, valence)  %>% summarize(mean_count = mean(count,na.rm=TRUE)))
  g = rbind(g, cbind(expand.grid(game_name=unique(g$game_name),level_number=unique(g$level_number), 
                                     event_type=unique(g$event_type), short_agent_type=unique(g$short_agent_type),
                                     valence=unique(g$valence)), mean_count=NA))
  p = ggplot(g,aes(x=event_type, y=mean_count, fill=short_agent_type))
  p=p+geom_bar(position='dodge',stat='identity')+theme(axis.text.x = element_text(angle = 90, hjust = 1))+facet_wrap(~level_number,ncol=1)+ggtitle(game)+
  scale_fill_manual(name="short_agent_type", values=colors)+ylab('mean no. of interactions')
  # p
  newdir='~/Projects/atari/vgdl/interaction_plots/by_event_type/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=10, height=15)  
}


## normalized by agent interactions
for (game in unique(data_with_valence$game_name)){
  
  # game_data = filter(data_with_valence, game_name==game, grepl('avatar', event_type), short_agent_type!='e-greedy')
  game_data = filter(data_with_valence, game_name==game, grepl('avatar', event_type))
  

  g=data.frame(game_data %>% group_by(game_name, level_number, event_type, short_agent_type, valence)  %>% summarize(mean_count = mean(count,na.rm=TRUE)))
  g = rbind(g, cbind(expand.grid(game_name=unique(g$game_name),level_number=unique(g$level_number), 
                                 event_type=unique(g$event_type), short_agent_type=unique(g$short_agent_type),
                                 valence=unique(g$valence)), mean_count=0))
  
  
  sum_data_for_game = data.frame(short_agent_type=as.character(), game_name=as.character(), level_number=as.numeric(), event_type=as.character(), per_level_normalized_count=as.numeric())
  
  for (agent in unique(g$short_agent_type)){
    agent_data = filter(g, short_agent_type==agent)
    for (level in unique(g$level_number)){
      level_agent_data = filter(agent_data, level_number==level)
      z = sum(level_agent_data$mean_count)
      for (event in unique(level_agent_data$event_type)){
        event_level_agent_sum = sum(filter(level_agent_data, event_type==event)$mean_count) ## you're taking the sum here because you had artificially inflated the data frame to contain 0 entries
        row = data.frame(short_agent_type=agent, game_name=game, level_number=level, event_type=event, per_level_normalized_count=event_level_agent_sum/z)
        sum_data_for_game = rbind(sum_data_for_game, row)
        }
    }
  }
  p = ggplot(sum_data_for_game,aes(x=event_type, y=per_level_normalized_count, fill=short_agent_type))
  p=p+geom_bar(position='dodge',stat='identity')+theme(axis.text.x = element_text(angle = 90, hjust = 1))+facet_wrap(~level_number,ncol=1)+ggtitle(game)+
    scale_fill_manual(name="short_agent_type", values=colors)+ylab('mean no. of interactions')
  # p
  newdir='~/Projects/atari/vgdl/interaction_plots/by_event_type_normalized/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=10, height=15)  
}


game_data = filter(data_with_valence, game_name==game, grepl('avatar', event_type), short_agent_type!='e-greedy')



####################
####################
# Helper functions #
####################
####################

remove_string_from_name = function(name){
  strings_to_remove = c('gvgai_variant','expt_variant','variant_expt', 'variant','gvgai', 'expt')
  for (i in 1:length(strings_to_remove)){
    string_to_remove = strings_to_remove[i]
    if (grepl(string_to_remove, name)){
      keep = substr(name, nchar(string_to_remove)+2, nchar(name))
      return(keep)
    }
    else{
      keep=name
    }
  }
  return(name)
}

load_data = function(data_to_load, dates_or_groups){
  data = list()
  for (date_or_group in dates_or_groups){
    if (data_to_load == 'EMPA'){
      filename = paste('~/Projects/atari/vgdl/',date_or_group, '/csv_data/interaction_data', sep='')
    }else if (data_to_load == 'human'){
      filename = paste('~/Projects/atari/vgdl/vgdl/human_interaction_data/', date_or_group, sep='')
      print(filename)
    }else if (data_to_load == 'DDQN'){
      filename = paste(dqn_path, '/', date_or_group, sep='')
    }
    
    d=read.csv(filename, header=TRUE, na.strings='NA')
    
    if (data_to_load=='DDQN' & grepl('100k', date_or_group)){
      d$agent_type = 'DDQN 100k'
    }else if (data_to_load=='DDQN' & grepl('10k', date_or_group)){
      d$agent_type = 'DDQN 10k'
    }else if (data_to_load=='DDQN' & grepl('1k', date_or_group)){
      d$agent_type = 'DDQN 1k'
    }else{
      hi='hi'
    }
    if (data_to_load=='DDQN' & grepl('seed', date_or_group)){
      start = unlist(gregexpr('seed', date_or_group))
      stop = start+nchar('seed')
      d$subject_ID = substring(date_or_group, start, stop)
    }
    
    if(length(data)==0){
      data = d
    }else{
      for(colname in names(d)){
        if (!(colname %in% names(data))){
          data[,colname] = NA
        }
      }
      for(colname in names(data)){
        if(!(colname %in% names(d))){
          d[,colname]=NA
        }
      }
      # print('about to rbind')
      data = rbind(data,d)
    }
  }
  
  data$modelrun_ID = as.factor(data$modelrun_ID)
  data$agent_type = as.factor(data$agent_type)
  data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
  if (data_to_load=='EMPA'){
    data$episode_number = as.character(data$episode_number)
    data$event_type=as.factor(data$event_type)
  }else if (data_to_load=='human'){
    data$episode_number = as.character(data$episode_number)
    data$event_type=as.factor(data$event_type)
  }else if (data_to_load=='DDQN'){
    data$episode_number = as.character(data$episode_number)
    data$event_type=as.factor(data$event_name)
    data$level_number = as.factor(data$game_level)
    data = select(data, -event_name, -game_level)
    # print('you need to take care of subject_ID for DDQN')
  }
  ## note: episode_number isn't actually a thing; that's not what you recorded for EMPA.
  ## deleting it to avoid confusion
  # data = select(data, -episode_number)
  data$short_agent_type = NA
  if (data_to_load =='human'){
    data$short_agent_type = as.factor(data_to_load)
  }else if (data_to_load == 'DDQN'){
    data$short_agent_type = data$agent_type
  }else if (data_to_load == 'EMPA'){
    e_greedy_05='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_1a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_1b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    
    # rand_policy='IW=1_rand=True_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      
    if (e_greedy_1a %in% unique(data$agent_type)){
        data[data$agent_type==e_greedy_1a,]$short_agent_type = 'e-greedy .1'
    }
    if (e_greedy_1b %in% unique(data$agent_type)){
      data[data$agent_type==e_greedy_1b,]$short_agent_type = 'e-greedy .1'
    }
    if (e_greedy_05 %in% unique(data$agent_type)){
        data[data$agent_type==e_greedy_05,]$short_agent_type = 'e-greedy .05'
      }
    for (agent in unique(data$agent_type)){
        if (grepl('rand=True', agent)){
          data[grepl('rand=True', data$agent_type),]$short_agent_type = 'random policy'
        }
      }
      if (NA %in% unique(data$short_agent_type)){
        data[is.na(data$short_agent_type),]$short_agent_type = 'EMPA'
      }

  }
  data = select(data, -agent_type) ## remove agent_type. too long.
  # sort the names into a canonical order.
  data = data[,c("subject_ID", "modelrun_ID", "game_name", "level_number", "event_type", "count","short_agent_type")]
  # add zero-count interactions. NOTE: this may take a long time if you're going through a lot of data. Should be optimized.
  data = add_zero_count_interactions(interactiondata=data)
  return (data)
  }

### Find all the interaction names that could exist for each game (that include the avatar),
### and add 0-count interactions for each subject-episode_number combination that doesn't contain them.
add_zero_count_interactions = function(interactiondata){
  outputframe = interactiondata
  for (game in unique(interactiondata$game_name)){
    game_subset = filter(interactiondata, game_name==game)
    episode_numbers = unique(game_subset$episode_number)
    all_event_types = unique(game_subset$event_type)
    avatar_event_types = all_event_types[grepl('avatar', all_event_types)]
    for (subject in unique(game_subset$subject_ID)){
      print(subject)
      agent_data = filter(game_subset, subject_ID==subject)
      agent_type = unique(agent_data$agent_type)[1]
      modelrun_ID = unique(agent_data$modelrun_ID)[1]
      short_agent_type = unique(agent_data$short_agent_type)[1]
      for (episode in episode_numbers){
        print(episode)
        subject_episode_combo = filter(game_subset, subject_ID==subject, episode_number==episode)
        ### if this has length 0 then you need to go through all the episode numbers and add rows.
        for (event_type in avatar_event_types){
          if (!(event_type %in% unique(subject_episode_combo$event_type))){
            row = data.frame(agent_type = agent_type, 
                             subject_ID=subject, 
                             modelrun_ID = modelrun_ID, 
                             game_name = game,
                             level_number = NA, 
                             event_type = event_type, 
                             count = 0, 
                             episode_number = episode, 
                             short_agent_type = short_agent_type,
                             game_level=NA)
            outputframe = rbind(outputframe, row)
          }
        }
      }
    }
  }
  return(outputframe)
}


add_valence_to_data = function(interactiondata){
  outdata = data.frame(subject_ID=as.character(), modelrun_ID=as.character(), game_name=as.character(), 
                       level_number=as.numeric(), event_type=as.character(), count=as.numeric(), short_agent_type=as.character(), valence=as.character())
  for (game in unique(interactiondata$game_name)){
    data = filter(interactiondata, game_name==game)
    if (grepl('aliens', game)){
      data$valence = ifelse(grepl('alien', data$event_type), 'negative',
                            ifelse(grepl('bomb', data$event_type), 'negative',
                                   ifelse(grepl('sam', data$event_type), 'instrumental',
                                                                      'neutral')))
    }else if (grepl('avoidgeorge', game)){
      data$valence = ifelse(grepl('george', data$event_type), 'negative',
                            'neutral')
    }else if (grepl('bait', game)){
      data$valence = ifelse(grepl('hole', data$event_type), 'negative',
                            ifelse(grepl('box', data$event_type), 'instrumental',
                                   ifelse(grepl('leftPistol', data$event_type), 'instrumental',
                                          ifelse(grepl('downPistol', data$event_type), 'instrumental',
                                                 ifelse(grepl('mold', data$event_type), 'instrumental',
                                                      ifelse(grepl('key', data$event_type), 'positive',
                                                          ifelse(grepl('mushroom', data$event_type), 'positive',
                                                              ifelse(grepl('goal', data$event_type), 'positive',
                                                 'neutral'))))))))
    }else if (grepl('bees_and_birds', game)){
      data$valence = ifelse(grepl('bee', data$event_type), 'negative',
                            ifelse(grepl('obstacle', data$event_type), 'negative',
                                   ifelse(grepl('fence', data$event_type), 'instrumental',
                                      ifelse(grepl('goal', data$event_type), 'positive',
                                          'neutral'))))
    }else if (grepl('boulderdash', game)){
      print ('got to boulderdash')
      data$valence = ifelse(grepl('butterfly', data$event_type), 'negative',
                                   ifelse(grepl('crab', data$event_type), 'negative',
                                        ifelse(grepl('dirt', data$event_type), 'instrumental',
                                              ifelse(grepl('diamond', data$event_type), 'positive',
                                                 ifelse(grepl('exitdoor', data$event_type), 'positive',
                                                        'neutral')))))
    }else if (game == 'butterflies'){
      data$valence = ifelse(grepl('butterfly', data$event_type), 'positive',
                            'neutral')
    }else if (grepl('butterflies_1', game)){
      data$valence = ifelse(grepl('butterfly', data$event_type), 'positive',
                            'neutral')
    }else if (grepl('butterflies_2', game)){
      data$valence = ifelse(grepl('butterfly', data$event_type), 'positive',
                                   'neutral')
    }else if (game %in% c('chase', 'chase_1')){
      data$valence = ifelse(grepl('angry', data$event_type), 'negative',
                            ifelse(grepl('scared', data$event_type), 'positive',
                                   'neutral'))
    }else if (game %in% c('chase_2', 'chase_3')){
      data$valence = ifelse(grepl('angry', data$event_type), 'negative',
                            ifelse(grepl('wolf', data$event_type), 'negative',
                                   ifelse(grepl('missile1', data$event_type), 'positive',
                                          ifelse(grepl('missile2', data$event_type), 'positive',
                                            ifelse(grepl('scared', data$event_type), 'positive',
                                          'neutral')))))
    }else if (game %in% c('closing_gates')){
      data$valence = ifelse(grepl('goal', data$event_type), 'positive',
                            'neutral')
    }else if (game %in% ('closing_gates_1')){
      data$valence = ifelse(grepl('goal', data$event_type), 'positive',
                            ifelse(grepl('boulder', data$event_type), 'instrumental',
                            'neutral'))
    }
    else if (grepl('corridor', game)){
      data$valence = ifelse(grepl('fastL', data$event_type), 'negative',
                            ifelse(grepl('mediumL', data$event_type), 'negative',
                                   ifelse(grepl('slowL', data$event_type), 'negative',
                                          ifelse(grepl('fastR', data$event_type), 'negative',
                                                 ifelse(grepl('mediumR', data$event_type), 'negative',
                                                        ifelse(grepl('slowR', data$event_type), 'negative',
                                                               ifelse(grepl('goal', data$event_type), 'positive',
                                                                      'neutral')))))))
    }else if (game %in% c('antagonist', 'antagonist_1', 'antagonist_2')){
      data$valence = ifelse(grepl('box1', data$event_type), 'positive',
                            ifelse(grepl('box2', data$event_type), 'instrumental',
                                   ifelse(grepl('box3', data$event_type), 'instrumental',
                                          ifelse(grepl('forcefield', data$event_type), 'instrumental',
                                                 'neutral'))))
    }else if (game %in% c('ee', 'ee_1', 'ee_2')){
      data$valence = ifelse(grepl('chaser', data$event_type), 'negative',
                            ifelse(grepl('apple', data$event_type), 'positive',
                                   ifelse(grepl('blueberry', data$event_type), 'positive',
                                          ifelse(grepl('orange', data$event_type), 'positive',
                                                 ifelse(grepl('dough', data$event_type), 'positive',
                                                        ifelse(grepl('eel', data$event_type), 'positive',
                                                               ifelse(grepl('fruit', data$event_type), 'positive',
                                                                      'neutral'))))))) 
    }else if (game == 'ee_3'){
      data$valence = ifelse(grepl('cranberry', data$event_type), 'negative',
                            ifelse(grepl('apple', data$event_type), 'positive',
                                   ifelse(grepl('blueberry', data$event_type), 'positive',
                                          ifelse(grepl('orange', data$event_type), 'positive',
                                                 ifelse(grepl('dough', data$event_type), 'positive',
                                                        ifelse(grepl('eel', data$event_type), 'positive',
                                                               ifelse(grepl('fruit', data$event_type), 'positive',
                                                                      'neutral'))))))) 
    }else if (grepl('frogs', game)){
      data$valence = ifelse(grepl('water', data$event_type), 'negative',
                            ifelse(grepl('slowRtruck', data$event_type), 'negative',
                                   ifelse(grepl('fastRtruck', data$event_type), 'negative',
                                          ifelse(grepl('slowLtruck', data$event_type), 'negative',
                                                 ifelse(grepl('fastLtruck', data$event_type), 'negative',
                                                        ifelse(grepl('log', data$event_type), 'instrumental',
                                                               ifelse(grepl('entry', data$event_type), 'instrumental',
                                                                      ifelse(grepl('exit1', data$event_type), 'instrumental',
                                                                             ifelse(grepl('bridge', data$event_type), 'instrumental',
                                                                                    ifelse(grepl('goal', data$event_type), 'positive',
                                                               'neutral'))))))))))
    }else if (grepl('lemmings', game)){
      data$valence = ifelse(grepl('hole', data$event_type), 'negative',
                            ifelse(grepl('snake', data$event_type), 'negative',
                                   ifelse(grepl('mole', data$event_type), 'negative',
                                          'neutral')))
    }else if (game == 'missilecommand_2'){
      data$valence = ifelse(grepl('explosion', data$event_type), 'negative',
                            'neutral')
    }else if (game == 'missilecommand_3'){
      data$valence = ifelse(grepl('incoming_slow', data$event_type), 'negative',
                            ifelse(grepl('incoming_fast', data$event_type), 'negative',
                                   'neutral'))
    }else if (grepl('myAliens', game)){
      data$valence = ifelse(grepl('ghost', data$event_type), 'negative',
                            ifelse(grepl('gate', data$event_type), 'positive',
                                   ifelse(grepl('alien', data$event_type), 'positive',
                                          'neutral')))
    }else if (grepl('plaqueattack', game)){
      data$valence = ifelse(grepl('deadMolarInf', data$event_type), 'positive',
                            ifelse(grepl('deadMolarSup', data$event_type), 'positive',
                                   ifelse(grepl('adversary', data$event_type), 'negative',
                                          ifelse(grepl('laser', data$event_type), 'negative',
                                                 'neutral'))))
    }else if(grepl('portals', game)){
      data$valence = ifelse(grepl('sitting', data$event_type), 'negative',
                            ifelse(grepl('random', data$event_type), 'negative',
                                   ifelse(grepl('chaser', data$event_type), 'negative',
                                          ifelse(grepl('vertical', data$event_type), 'negative',
                                                 ifelse(grepl('horizontal', data$event_type), 'negative',
                                                        ifelse(grepl('entry1', data$event_type), 'instrumental',
                                                               ifelse(grepl('entry2', data$event_type), 'instrumental',
                                                                      ifelse(grepl('entry3', data$event_type), 'instrumental',
                                                                             ifelse(grepl('exit1', data$event_type), 'instrumental',
                                                                                    ifelse(grepl('exit2', data$event_type), 'instrumental',
                                                                                           ifelse(grepl('exit3', data$event_type), 'instrumental',
                                                                                                  ifelse(grepl('goal', data$event_type), 'positive',
                                                                                                         'neutral'))))))))))))
    }else if (grepl('preconditions', game)){
      data$valence = ifelse(grepl('goal', data$event_type), 'positive',
                            ifelse(grepl('medicine', data$event_type), 'instrumental',
                                   ifelse(grepl('poison', data$event_type), 'negative',
                                                 'neutral')))
    }else if (game %in% c('push_boulders', 'push_boulders_1')){
      data$valence = ifelse(grepl('poison1', data$event_type), 'negative',
                            ifelse(grepl('poison2', data$event_type), 'negative',
                                   ifelse(grepl('poison3', data$event_type), 'negative',
                                          ifelse(grepl('box1', data$event_type), 'instrumental',
                                                 ifelse(grepl('dynamite', data$event_type), 'instrumental',
                                                        ifelse(grepl('goal', data$event_type), 'positive',
                                                 'neutral'))))))
    }else if (game %in% c('push_boulders_2')){
      data$valence = ifelse(grepl('poison1', data$event_type), 'negative',
                            ifelse(grepl('poison2', data$event_type), 'negative',
                                   ifelse(grepl('poison3', data$event_type), 'negative',
                                          ifelse(grepl('box1', data$event_type), 'instrumental',
                                                 ifelse(grepl('fuseright', data$event_type), 'instrumental',
                                                        ifelse(grepl('fuseup', data$event_type), 'instrumental',
                                                               ifelse(grepl('litfuseright', data$event_type), 'instrumental',
                                                                      ifelse(grepl('litfuseup', data$event_type), 'instrumental',
                                                                             ifelse(grepl('goal', data$event_type), 'positive',
                                                               'neutral')))))))))
    }else if (game=='relational'){
      data$valence = ifelse(grepl('probe', data$event_type), 'instrumental',
                            ifelse(grepl('converter1', data$event_type), 'instrumental',
                                   ifelse(grepl('fire', data$event_type), 'instrumental',
                                          ifelse(grepl('box1', data$event_type), 'instrumental',
                                                 ifelse(grepl('converter3', data$event_type), 'instrumental',
                                                        'neutral')))))
    }else if (game%in%c('relational_1', 'relational_2')){
      data$valence = ifelse(grepl('converter1', data$event_type), 'instrumental',
                            ifelse(grepl('box1', data$event_type), 'instrumental',
                                   ifelse(grepl('converter3', data$event_type), 'instrumental',
                                          'neutral')))
    }else if (grepl('sokoban', game)){
      data$valence = ifelse(grepl('box', data$event_type), 'instrumental',
                            ifelse(grepl('hole', data$event_type), 'instrumental',
                                   ifelse(grepl('fence', data$event_type), 'instrumental',
                                          ifelse(grepl('portal1', data$event_type), 'instrumental',
                            'neutral'))))
    }else if (game=='surprise'){
      data$valence = ifelse(grepl('apple', data$event_type), 'positive',
                                   'neutral')
    }else if (game=='surprise_1'){
      data$valence = ifelse(grepl('apple', data$event_type), 'positive',
                                   ifelse(grepl('inert', data$event_type), 'negative',
                                                                      'neutral'))
    }else if (game=='surprise_2'){
      data$valence = ifelse(grepl('inert', data$event_type), 'positive',
                                                 'neutral')
    }else if (game%in%c('survivezombies','survivezombies_1')){
      data$valence = ifelse(grepl('honey', data$event_type), 'positive',
                            ifelse(grepl('slowHell', data$event_type), 'negative',
                                   ifelse(grepl('fastHell', data$event_type), 'negative',
                                          ifelse(grepl('zombie', data$event_type), 'negative',
                                          'neutral'))))
    }else if (game=='survivezombies_2'){
      data$valence = ifelse(grepl('honey', data$event_type), 'positive',
                            ifelse(grepl('slowHell', data$event_type), 'negative',
                                   ifelse(grepl('fastHell', data$event_type), 'negative',
                                          ifelse(grepl('zombie', data$event_type), 'positive',
                                                 'neutral'))))
    }else if (grepl('watergame', game)){
      data$valence = ifelse(grepl('door', data$event_type), 'positive',
                            ifelse(grepl('box', data$event_type), 'instrumental',
                                   ifelse(grepl('antibox', data$event_type), 'instrumental',
                                          ifelse(grepl('part1', data$event_type), 'instrumental',
                                                 ifelse(grepl('part2', data$event_type), 'instrumental',
                                                        ifelse(grepl('water', data$event_type), 'negative',
                                                               ifelse(grepl('fastHell', data$event_type), 'negative',
                                                                      'neutral')))))))
    }else if (grepl('zelda', game)){
      data$valence = ifelse(grepl('monsterQuick', data$event_type), 'negative',
                            ifelse(grepl('monsterNormal', data$event_type), 'negative',
                                   ifelse(grepl('monsterSlow', data$event_type), 'negative',
                                          ifelse(grepl('key', data$event_type), 'instrumental',
                                                 ifelse(grepl('goal', data$event_type), 'positive',
                                                        'neutral')))))
    }else{
      data$valence = NA
      print ('did not find game')
      ## omitting jaws (bc shark interactions are good/bad depending on what avatar is carrying)
      ## omitting missilecommand 0 1 4 because there are no direct avatar interactions that are good/bad
      ## omitting helper
    }
    print(game)
    outdata = rbind(outdata, data)
  }
  return(outdata)
}

excluded_games = c('jaws', 'jaws_1', 'jaws_2','missilecommand', 'missilecommand_1', 'missilecommand_4', 'helper', 'helper_1', 'helper_2')

make_sum_dataframes = function(data){
  sum_dataframe = data.frame(short_agent_type=as.character(), game_name=as.character(), level=as.numeric(), valence=as.character(), raw_count=as.numeric(),
                                          across_level_normalized_count=as.numeric(), per_level_normalized_count=as.numeric())
  for (game in unique(data$game_name)){
    game_data = filter(data, game_name==game)
    sum_data = make_sum_dataframe(game_data, game)
    sum_dataframe = rbind(sum_dataframe, sum_data)
  }
  return(sum_dataframe)
}

cross_entropy = function(p, q, constant){
  p = as.numeric(p)
  q = as.numeric(q)
  p = p+constant
  q = q+constant
  p = p/sum(p)
  q = q/sum(q)
  # if (0 %in% p){
  #   p = p+0.01
  #   p = p/sum(p)
  # }
  # if (0 %in% q){
  #   q = q+0.01
  #   q = q/sum(q)
  # }
  s = 0
  for (i in 1:length(p)){
    s = s - p[i]*log(q[i], 2)
  }
  return (s)
}
make_sum_dataframe = function(data, game_name){
  sum_data = data.frame(short_agent_type=as.character(), game_name=as.character(), level=as.numeric(), valence=as.character(), raw_count=as.numeric(),
                        across_level_normalized_count=as.numeric(), per_level_normalized_count=as.numeric(),
                        across_level_no_neutral_normalized_count=as.numeric(), per_level_no_neutral_normalized_count=as.numeric())
  for (agent in unique(data$short_agent_type)){
    agent_data = filter(data, short_agent_type==agent, grepl('avatar', event_type))
    z = sum(agent_data$count)
    z_no_neutral = sum(filter(agent_data, valence!='neutral')$count)
    for (vlc in c('positive','instrumental','neutral', 'negative')){
      across_level_cnt = sum(filter(agent_data, valence==vlc)$count)
      if(vlc=='neutral'){
        across_level_no_neutral_cnt = NA
      }else{
        across_level_no_neutral_cnt = across_level_cnt
      }
      for (level in unique(agent_data$level)){
        agent_level_data = filter(agent_data, level_number==level)
        agent_level_no_neutral_data = filter(agent_data, level_number==level, valence!='neutral')
        z_1 = sum(agent_level_data$count)
        z_2 = sum(agent_level_no_neutral_data$count)
        per_level_cnt = sum(filter(agent_level_data, valence==vlc)$count)
        if(vlc=='neutral'){
          per_level_cnt_for_no_neutral = NA
        }else{
          per_level_cnt_for_no_neutral = per_level_cnt
        }
        row = data.frame(short_agent_type=agent, game_name=game_name, level=level, valence=vlc, raw_count=per_level_cnt,
                         across_level_normalized_count=across_level_cnt/z, per_level_normalized_count=per_level_cnt/z_1, 
                         across_level_no_neutral_normalized_count=across_level_no_neutral_cnt/z_no_neutral,
                         per_level_no_neutral_normalized_count=per_level_cnt_for_no_neutral/z_2)
        sum_data = rbind(sum_data, row)
      }    
    }
    
  }
  # sum_data = transform(sum_data, short_agent_type=factor(short_agent_type, levels=c("human", "EMPA", "DDQN")))
  # df = filter(df, !is.na(short_agent_type))
  # df = transform(df, short_agent_type=factor(short_agent_type, levels=c("human", "EMPA", "DDQN", "e-greedy")))
  return(sum_data)
}


calculate_distance = function(v1,v2,metric,constant){
  ## constant is only used for cross-entropy
  v1=as.numeric(v1)
  v2=as.numeric(v2)
  
  if (missing(constant)){
    constant = ''
  }
  
  if (metric=='cosine'){
    return(cosine(v1,v2))
  }
  else if (metric=='avg_absolute_difference'){
    return(mean(abs(v1-v2)))
  }
  else if (metric=='avg_squared_difference'){
    return(mean((v1-v2)**2))
  }
  else if (metric=='cross-entropy'){
    return(cross_entropy(v1, v2, constant))
  }
}

calculate_proportion_of_games_best_fit_by_each_model = function(distance_df){
  counts=c()
  games=c()
  for (game in unique(distance_df$game_name)){
    game_data = filter(distance_df, game_name==game)
    if (!is.nan(sum(as.numeric(as.character(game_data$distance)), na.rm=TRUE)) & sum(as.numeric(as.character(game_data$distance)),na.rm=TRUE)>0){
      counts = c(counts,as.character(game_data[game_data$distance==min(as.numeric(as.character(game_data$distance))),]$type))
      games=c(games, game)
    }
  }
  counts=na.omit(counts)
  absolute_normalized_counts = data.frame(type=as.character(), normalized_count=as.numeric(), metric=as.character())
  z=length(counts)
  for (corr_type in unique(counts)){
    row = data.frame(type=corr_type, normalized_count=sum(counts==corr_type)/z, metric=distance_df$metric[1])
    absolute_normalized_counts = rbind(absolute_normalized_counts, row)
  }
  return(absolute_normalized_counts)
}

find_best_model = function(distance_df){
  best_model_df = data.frame(game_name=as.character(), best_model=as.character(), margin=as.numeric())
  for (game in unique(distance_df$game_name)){
    game_data = filter(distance_df, game_name==game)
    best = min(as.numeric(as.character(game_data$distance)))
    second_best = as.numeric(as.character(sort(game_data$distance,decreasing=FALSE)[2]))
    margin = second_best - best
    row = game_data[as.numeric(as.character(game_data$distance))==best,][c('game_name', 'type', 'metric')]
    row$margin = margin
    best_model_df = rbind(best_model_df, row)
  }
  return(best_model_df)
}


###SCRAPS###
# 
# corr_frame = data.frame(game_name=as.character(), human_empa=as.numeric(), empa_random=as.numeric(), empa_e_greedy=as.numeric(), 
#                         human_random=as.numeric(), human_e_greedy=as.numeric(), random_e_greedy=as.numeric())
# corr_frame = rbind(corr_frame, cbind(as.character(unique(corr_dataframe$game_name)),human_empa, EMPA_random, EMPA_e_greedy, human_random, human_e_greedy, random_e_greedy))
# names(corr_frame)[1] = 'game_name'
# corr_frame$nearest_to_human = NA
# 
# col_names=c('human_empa', 'human_random', 'human_e_greedy')
# for (i in 1:length(corr_frame$game_name)){
#   row_vals = c(as.numeric(as.character(corr_frame[i,]$human_empa)), as.numeric(as.character(corr_frame[i,]$human_random)), as.numeric(as.character(corr_frame[i,]$human_e_greedy)))
#   if (metric %in% c('avg_absolute_difference', 'avg_squared_difference')){
#     corr_frame$nearest_to_human[i] = col_names[row_vals==min(row_vals)]
#   }else{
#     corr_frame$nearest_to_human[i] = col_names[row_vals==max(row_vals)]
#   }
# }
# 
# # abs_distances = corr_frame
# squared_distances = corr_frame

## preparing to plot distribution of distances from second-best
# distance_frame = data.frame(game_name=as.character(), type=as.character(), distance=as.numeric)
# for (game in unique(corr_frame$game_name)){
#   for (model_type in unique(corr_frame_vert$type)){
#     relevant_row = filter(corr_frame, game_name==game)
#     row_vals = c(as.numeric(as.character(relevant_row$human_empa)), as.numeric(as.character(relevant_row$human_random)), as.numeric(as.character(relevant_row$human_e_greedy)))
#     second_best = as.numeric(as.character(sort(row_vals,decreasing=FALSE)[2]))
#     model_score = as.numeric(as.character(relevant_row[,which(names(corr_frame)==model_type)]))
#     d_from_s = model_score - second_best
#     row = data.frame(game_name=game, type=model_type, distance=d_from_s)
#     distance_frame = rbind(distance_frame, row)
#   }
# }
# ## distribution of distances from second-best
# p = ggplot(distance_frame, aes(x=distance, fill=type))
# p = p+geom_density(alpha=.4)+geom_vline(xintercept=0,linetype='dashed',size=.4) +ggtitle('Margin over second-best model, by model')
# p

# 
# normalized_counts = data.frame(type=as.character(), count=as.numeric())
# z=sum(!is.na(corr_frame$nearest_to_human))
# for (i in 1:length(col_names)){
#   row=data.frame(type=as.character(col_names[i]), count=sum(!is.na(corr_frame$nearest_to_human) & corr_frame$nearest_to_human==col_names[i])/z)
#   normalized_counts=rbind(normalized_counts, row)
# }
# 
# ## Plot proportion of times that each model best fits human data
# p = ggplot(transform(normalized_counts, type=factor(type, levels=c('human_empa','human_e_greedy','human_random'))), aes(x=type, y=count))
# p = p+geom_bar(stat='identity')+scale_x_discrete(breaks=c('human_empa','human_e_greedy','human_random'),
#                                                  labels=c("EMPA", "e-greedy", "random policy"))+
#   ylab('Proportion')+xlab('Model')+ggtitle('Proportion of games best fit by model type')+ylim(0,.7)
# p

# ## Plot negative interactions for all games:
# for (game in unique(sum_dataframes$game_name)){
#   p = ggplot(filter(sum_dataframes, game_name==game, valence=='negative'), aes(x=level, y=raw_count, fill=short_agent_type))
#   p=p+geom_bar(stat='identity')+theme(axis.text.x = element_text(angle = 90, hjust = 1))+facet_wrap(~short_agent_type,ncol=1)+
#     ggtitle(paste('negative interactions: ',game,sep=''))+
#     scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count')
#   #p
#   
#   newdir='~/Projects/atari/vgdl/interaction_plots/negative_interactions_by_level/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, game, '.png', sep='')
#   ggsave(title, plot=p, width=15, height=10)  
# }
