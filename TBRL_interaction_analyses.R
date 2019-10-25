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
  ## add random policy again
  df = transform(filter(raw_count_df, game_name==game), short_agent_type=factor(short_agent_type, levels=c('human', 'EMPA', 'DDQN 100k')),
            valence=factor(valence, levels=c('positive', 'instrumental', 'neutral', 'negative')))
  
  p = ggplot(filter(df, !is.na(short_agent_type)),
             aes(x=valence, y=log(raw_count,10)+.05, fill=short_agent_type))+facet_wrap(~short_agent_type, ncol=1, drop=TRUE)
  p=p+geom_histogram(stat='summary', fun.y='mean', position='dodge')+
    scale_fill_manual(name="short_agent_type", values=colors)+ xlab('interaction valence')+ylab('interaction count (unnormalized)')+
    scale_y_continuous(breaks=logtickmarks, labels=tickmarks, limits=c(0,log(1000000,10)))+ggtitle(game)+theme(axis.text.x = element_text(angle = 90, hjust = 1))
  ## center ggtitle, remove background
  p = p+theme(panel.background = element_blank(), plot.title = element_text(hjust = 0.5))
  newdir='~/Projects/atari/vgdl/interaction_plots/by_valence_all_levels_unnormalized/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=5, height=8)
}


## Collisions with deadly objects.
### we only have data for 59 games bc that's the number of games that have negative interactions that we coded for.

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


## log scale per negative collision plot
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



####################
####################
# Helper functions #
####################
####################


load_interaction_data = function(data_to_load, dates_or_groups){
  data = list()
  for (date_or_group in dates_or_groups){
    if (data_to_load == 'EMPA'){
      filename = paste(getwd(),'/data_files/EMPA/', date_or_group,'/csv_data/interaction_data', sep='')
      # filename = paste('~/Projects/atari/vgdl/',date_or_group, '/csv_data/interaction_data', sep='')
    }else if (data_to_load == 'human'){
      filename = paste(getwd(),'/data_files/human_interaction_data/', date_or_group, sep='')
            # filename = paste('~/Projects/atari/vgdl/vgdl/human_interaction_data/', date_or_group, sep='')
    }else if (data_to_load == 'DDQN'){
      filename = paste(ddqn_interaction_path, '/', date_or_group, sep='')
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
      agent_data = filter(game_subset, subject_ID==subject)
      agent_type = unique(agent_data$agent_type)[1]
      modelrun_ID = unique(agent_data$modelrun_ID)[1]
      short_agent_type = unique(agent_data$short_agent_type)[1]
      for (episode in episode_numbers){
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
      ## omitting jaws (bc shark interactions are good/bad depending on what avatar is carrying)
      ## omitting missilecommand 0 1 4 because there are no direct avatar interactions that are good/bad
      ## omitting helper
    }
    outdata = rbind(outdata, data)
  }
  return(outdata)
}

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