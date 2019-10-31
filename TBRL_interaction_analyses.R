

###################
# Load data       #
###################
ddqn_interaction_path = paste(getwd(),'/data_files/ddqn_interaction_data/interaction_data', sep='')
ddqn_interaction_files = list.files(ddqn_interaction_path)
EMPA_interaction_dates = list('mar28', 'apr4')
human_interaction_files = list.files(paste(getwd(), '/data_files/human_interaction_data', sep=''))

## ddqn data
ddqn_100k_interactiondata=c()
for (d in ddqn_interaction_files){
  if (grepl('100k', d) & grepl('seed0', d)){
    ddqn_100k_interactiondata = c(ddqn_100k_interactiondata, d)
  }
}
ddqninteractiondata = load_interaction_data('DDQN', ddqn_100k_interactiondata) #takes a while
EMPAinteractiondata = load_interaction_data('EMPA', EMPA_interaction_dates)
humaninteractiondata = load_interaction_data('human', human_interaction_files)

interactiondata = rbind(humaninteractiondata, EMPAinteractiondata, ddqninteractiondata)

## add hand-coded valence
data_with_valence = add_valence_to_data(interactiondata)
sum_dataframes = make_sum_dataframes(data_with_valence)

excluded_games = c('jaws', 'jaws_1', 'jaws_2','missilecommand', 'missilecommand_1', 'missilecommand_4', 'helper', 'helper_1', 'helper_2')


interactioncolors = c('steelblue1', 'purple2', 'firebrick2', 'palegreen3',
           'gray50', 'gray52', 'gray54',
           'gray50', 'gray52', 'gray54')

names(interactioncolors)=c('EMPA', 'e-greedy', 'random', 'human', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k', 'DDQN', 'DDQN', 'DDQN')


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

## Raw counts of interactions (used for plotting)
## WARNING: This is slow
raw_count_df=data.frame(short_agent_type=as.character(), subject_ID=as.character(), game_name=as.character(), valence=as.character(), raw_count=as.numeric())
# tmp_dwv = filter(data_with_valence, short_agent_type%in%c('DDQN 100k', 'DDQN 10k', 'DDQN 1k'))
for (game in unique(data_with_valence$game_name)){
  game_data = filter(data_with_valence, game_name==game)
  for (subject in unique(game_data$subject_ID)){
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


normalized_abs_distance = create_distance_dataframe(normalized_per_agent_counts,'avg_absolute_difference')
normalized_abs_distance_best_models = find_best_model(normalized_abs_distance)

## Find games on which each model did best
empa_best = filter(normalized_abs_distance_best_models, type=='human_empa')
empa_best[order(empa_best$margin),]
ee_best[order(ee_best$margin),]
ddqn_best[order(ddqn_best$margin),]


normalized_abs_distance_best_models_with_cutoff = calculate_proportions(filter(normalized_abs_distance_best_models, type!='human_random'), margin_cutoff=0.2)
normalized_abs_distance$distance=as.numeric(as.character(normalized_abs_distance$distance))

static_games = c('push_boulders_2', 'push_boulders', 'push_boulders_1', 'preconditions', 'preconditions_1', 'preconditions_2', 'bait', 'bait_1', 'bait_2', 
                 'watergame', 'watergame_1', 'watergame_2', 'relational', 'sokoban', 'sokoban_1', 'sokoban_2', 'ee')

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


## supplementary figure comparing fast- and slow-paced games
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

### convert to format for ternary plot
games_used_in_12_plot = c(group1, group2)
max_distance = max(as.numeric(as.character(normalized_abs_distance$distance)))
human_empa = max_distance-as.numeric(as.character(filter(normalized_abs_distance, type=='human_empa')$distance))
human_e_greedy = max_distance-as.numeric(as.character(filter(normalized_abs_distance, type=='human_e_greedy')$distance))
human_ddqn = max_distance-as.numeric(as.character(filter(normalized_abs_distance, type=='human_ddqn')$distance))
game_names = filter(normalized_abs_distance, type=='human_empa')$game_name


## unnormalized interactions across levels, for each game
tickmarks = c(10,100,1000,10000,100000,1000000,10000000)
logtickmarks=c(.05,log(tickmarks,10))
tickmarks = c(1,tickmarks)
for (game in unique(raw_count_df$game_name)){
  df = transform(filter(raw_count_df, game_name==game), short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'DDQN 100k')),
            valence=factor(valence, levels=c('positive', 'instrumental', 'neutral', 'negative')))
  
  p = ggplot(filter(df, !is.na(short_agent_type)),
             aes(x=valence, y=log(raw_count,10)+.05, fill=short_agent_type))+facet_wrap(~short_agent_type, ncol=1, drop=TRUE)
  p=p+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
    scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (unnormalized)')+
    scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,log(1000000,10)))+ggtitle(game)+theme(axis.text.x = element_text(angle = 90, hjust = 1))
  p = p+theme(panel.background = element_blank(), plot.title = element_text(hjust = 0.5))
  
  newdir = paste(getwd(),'/data_files/interaction_plots/by_valence_all_levels_unnormalized/', sep='')
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=5, height=8)
}


## Collisions with deadly objects.
### we only have data for 59 games bc that's the number of games that have negative interactions that we coded for.

game_df = data.frame(short_agent_type=as.character(), game_name=as.character(), count=as.numeric())
for (game in unique(data_with_valence$game_name)){
  game_data = filter(data_with_valence, game_name==game, valence=='negative', grepl('avatar', event_type))
  for (subject in unique(game_data$subject_ID)){
    short_agent_type = filter(game_data, subject_ID==subject)$short_agent_type[1]
    subject_data = filter(game_data, subject_ID==subject)
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

## log scale for negative collision plot
all_level_game_df$formatted_game_name = NA
for (i in 1:length(all_level_game_df$game_name)){
  all_level_game_df$formatted_game_name[i] = gsub('_',' ',all_level_game_df$game_name[i])
}

dqn_games = unique(filter(all_level_game_df, short_agent_type=='DDQN 100k')$formatted_game_name)
dqn_games=dqn_games[order(as.character(dqn_games))]

data_to_plot = filter(transform(all_level_game_df, short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k'))), formatted_game_name%in%dqn_games)
data_to_plot = filter(data_to_plot, !is.na(short_agent_type))

# data_to_plot$formatted_game_name = NA
# for (i in 1:length(data_to_plot$game_name)){
#   data_to_plot$formatted_game_name[i] = gsub('_',' ',data_to_plot$game_name[i])
# }

## Figure 6C
tickmarks = c(10,100,1000,10000,1e5,1e6)
logtickmarks=c(.05,log(tickmarks,10))
tickmarks = c(1,tickmarks)
levels(data_to_plot$short_agent_type) = c('human', 'EMPA', 'e-greedy','DDQN')
p = ggplot(filter(data_to_plot, short_agent_type%in%c('human','EMPA','DDQN')),
           aes(x=formatted_game_name, y=log(count,10)+.05, fill=short_agent_type))+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
  facet_wrap(~short_agent_type,ncol=1,strip.position='bottom',shrink=TRUE)+
  scale_fill_manual(name="short_agent_type", values=interactioncolors)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),
        axis.text.y=element_text(size=22),
        axis.title.y=element_text(size=24), axis.title.x=element_text(size=24), plot.title=element_text(size=26))+
  scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,5.5))+scale_x_discrete(limits=dqn_games)+theme(legend.position="none", panel.background = element_blank())+
 ylab('Interactions with deadly items')+xlab('Game name')#+ggtitle('Collisions with deadly objects')
p
## save as 12x12


