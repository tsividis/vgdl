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

## everything starting mar23 has no 15-loss cutoff.
## nov28 old planner-lesion data
## mar28: 10 runs of EMPA with no limit on losses.
## mar30: unclear
## apr4: e-greedy and random policy, both 10x. Random policy incomplete (got kicked off om2)
EMPA_dates = list('mar28', 'apr4')
lesion_dates = list('jun3', 'jun22', 'jun23')
planner_lesion_dates = list('nov28')
dqn_path = '~/Projects/atari/vgdl/dqn_data/'
rainbow_path = '~/Projects/atari/vgdl/rainbow_data/'

humandatapaths = list.files("~/Projects/atari/vgdl/humandata")


### Toggle the below line to alter what you're reading in
data_to_load = 'EMPA'
data_to_load = 'human'
data_to_load = 'DDQN'
data_to_load = 'rainbow'

if (data_to_load == 'EMPA'){
  dates_or_groups = EMPA_dates
}else if (data_to_load == 'human'){
  dates_or_groups = groups
}else if (data_to_load %in% c('DDQN','rainbow')){
  dates_or_groups = NA #doesn't matter
}

EMPAdata = load_reward_data('EMPA', dates_or_groups)

EMPA_variants = filter(EMPAdata, agent_type!='EMPA')
humandata = load_reward_data('human', dates_or_groups)
dqndata = load_reward_data('DDQN', dates_or_groups)
planner_lesions = load_reward_data('EMPA', list('nov28'))

rainbow_data = load_reward_data('rainbow', dates_or_groups)

## everything that is currently stored as e-greedy .1 is called e-greedy 2k in the new lesions

### Before you do this, you need to fix how you're IDing model types from the string. you've added new parts
## (minimally batchID).
first_lesions = load_reward_data("EMPA", c('apr4'))

new_lesions = load_reward_data('EMPA', c('apr4', 'jun3', 'jun22', 'jun23'))
# new_lesions_saved = new_lesions ##jun3
# new_lesions_2 = load_reward_data('EMPA', dates_or_groups)
# new_lesions_3 = load_reward_data('EMPA', dates_or_groups)
# new_lesions_all = rbind(new_lesions, new_lesions_2, new_lesions_3)
# new_lesions = load_reward_data('EMPA', lesion_dates)

## Used this to check which lesions didn't have enough data
for (agent in unique(new_lesions$agent_type)){
  agent_data = filter(new_lesions, agent_type==agent)
  for (game in unique(EMPAdata$game_name)){
    game_data = filter(agent_data, game_name==game)
    if (length(unique(game_data$subject_ID))<5){
    print (c(agent, game, (length(unique(game_data$subject_ID)))))
    }
  }
}


# new_lesions_5_each_2 = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
#                                 odelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
# for (agent in c('e-greedy 2k')){
#     agent_data = filter(new_lesions, agent_type==agent)
#     for (game in unique(EMPAdata$game_name)){
#       game_data = filter(agent_data, game_name==game)
#       first_5_IDs = unique(filter(game_data)$subject_ID)[1:5]
#       for (ID in first_5_IDs){
#         subject_data = filter(game_data, subject_ID==ID)
#         new_lesions_5_each_2 = rbind(new_lesions_5_each_2, subject_data)
#       }
#     }
# }
# 
# new_lesions_5_each = rbind(new_lesions_5_each, new_lesions_5_each_2)

## Grab first 5 of each lesion. This takes a *very* long time.
new_lesions_5_each = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
                                odelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
for (agent in unique(new_lesions$agent_type)){
  ## exclude two lesion types we ran by mistake:
  if (!(agent %in% c('e-greedy 1k SN', 'e-greedy 1k SS', 'EMPA'))){
    agent_data = filter(new_lesions, agent_type==agent)
    for (game in unique(EMPAdata$game_name)){
      game_data = filter(agent_data, game_name==game)
      first_5_IDs = unique(filter(game_data)$subject_ID)[1:5]
      for (ID in first_5_IDs){
        subject_data = filter(game_data, subject_ID==ID)
        new_lesions_5_each = rbind(new_lesions_5_each, subject_data)
      }
    }
  }
}
 
# human_normed_new_lesions_2 = make_human_normed_data(rbind(new_lesions_5_each_2, humandata))
# human_normed_new_lesions_2$model_cluster = NA
# human_normed_new_lesions_2$formatted_game_name = NA
# human_normed_new_lesions = rbind(human_normed_new_lesions, filter(human_normed_new_lesions_2, agent_type=='e-greedy 2k'))

new_lesions = rbind(new_lesions_5_each, humandata)
human_normed_new_lesions = make_human_normed_data(new_lesions)
saved_human_normed_new_lesions = human_normed_new_lesions
saved_human_normed_data = human_normed_data
human_normed_new_lesions$model_cluster = NA
human_normed_new_lesions$formatted_game_name = NA
human_normed_new_lesions = rbind(human_normed_new_lesions, filter(human_normed_data, agent_type%in%c('EMPA', 'DDQN 100k')))
human_normed_data = rbind(human_normed_new_lesions, filter(human_normed_data, agent_type %in% c('DDQN 1k', 'DDQN 10k')))

## august 4:
saved_human_normed_data = human_normed_data ## human DDQN 100k EMPA 
rainbow_and_humans = rbind(rainbow_data, humandata)
human_normed_rainbow_data = make_human_normed_data(rainbow_and_humans)
human_normed_data = select(human_normed_data, -formatted_game_name)
human_normed_data = rbind(human_normed_data, filter(human_normed_rainbow_data, agent_type!='human'))
#####

# human_normed_new_lesions_2 = rbind(human_normed_new_lesions, human_normed_data)

p = ggplot(filter(human_normed_new_lesions, agent_type!='human'), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed Efficiency") + ylab("Density") +
  geom_vline(xintercept=0,linetype='dashed',size=.4)+facet_wrap(~agent_type, ncol=1)
p # 12x10


savedalldata = alldata
# dqndata = data
alldata = rbind(EMPAdata, planner_lesions, humandata, dqndata)
#EMPA_data = filter(alldata, agent_type=='EMPA')
# alldata = filter(alldata, agent_type!='EMPA')
# alldata = rbind(alldata, filter(EMPAdata, agent_type=='EMPA'))
#saved_human_normed_data = human_normed_data

## To calculate human-normed data for just some new model, do something like this.
## Note: you'll always need to pass humans in.
# just_empa_and_humans = filter(alldata, agent_type%in%c('human', 'EMPA'))
# human_normed_data_just_empa_and_humans = make_human_normed_data(just_empa_and_humans)
## now putting these back in:
# human_normed_data = filter(human_normed_data, agent_type!='EMPA')
# human_normed_data = select(human_normed_data, -model_cluster)
# human_normed_data = rbind(human_normed_data, filter(human_normed_data_just_empa_and_humans, agent_type=='EMPA'))

# planner_lesions_plus_humans = make_human_normed_data(rbind(humandata, planner_lesions))
# planner_lesions_plus_humans = filter(planner_lesions_plus_humans, !(agent_type%in%c('EMPA', 'human')))


saved_human_normed_data = human_normed_data
just_empa_and_humans = make_human_normed_data(rbind(humandata, data))

human_normed_data = make_human_normed_data(filter(alldata, agent_type %in% c('human', 'EMPA', 'DDQN 100k')))

## Finds all (subject, game, level) tuples where the subject was forced to play a level more than once.
fullhumandata = load_full_human_data()
excluded_subjects = data.frame(game_name=as.character(), subject_ID=as.character(), level=as.numeric())
for (game in unique(fullhumandata$game_name)){
  human_game_data = filter(fullhumandata, game_name==game)
  for (subject in unique(human_game_data$subject_ID)){
    subject_data = filter(human_game_data, subject_ID==subject)
    for (level in unique(subject_data$level_number)){
      if (length(unique(filter(subject_data, level_number==level)$cumulative_wins))>2){
        excluded_subjects = rbind(excluded_subjects, data.frame(game_name=game, subject_ID=subject, level_number=level))
      }
    }
  }
}


# zelda_data = filter(EMPA_variants, agent_type=='e-greedy .1', game_name=='zelda')
# for (subject in unique(zelda_data$subject_ID)){
#   print (c(subject, max(filter(zelda_data, subject_ID==subject)$level_number)))
# }

# colors = c('steelblue1', #EMPA
#            'purple1', 'purple2', 'purple3', 'purple4', #e-greedy
#            'firebrick2',# 'seagreen3','darkolivegreen1',
#            'palegreen3',# 'tomato2', 'salmon', 
#            'gray50', 'gray52', 'gray54',
#            'goldenrod1', 'goldenrod3', 'darkslategray2', 'goldenrod2', 'darkolivegreen3')
#            # 'darkslategray3', 'darkslategray2', 'darkslategray1')#, 'mediumpurple2', 'aquamarine3', 'coral3')
# ## change this
# names(colors)=unique(alldata$agent_type)



p = ggplot(human_normed_data, aes(x=agent_type, y=mean_levels_won))
p=p+geom_bar(stat='summary', fun.y='mean')
p

### To make plots for figure 3 (learning curves)
## plotting all agents/models
games_to_plot = c('avoidgeorge','bait', 'butterflies', 'frogs', 'zelda', 'missilecommand', 'plaqueattack')
# games_to_plot = c('avoidgeorge_4', 'bait_2', 'ee_2', 'ee_3', 'frogs', 'surprise_1', 'zelda_2', 'corridor')
games_in_order = unique(alldata$game_name)[order(unique(alldata$game_name))]
plots = list()
# for(k in 1:length(unique(alldata$game_name))){
for (k in 1:length(games_to_plot)){
  agents_to_plot = c('human', 'DDQN 100k', 'EMPA')
  # game = games_in_order[k]
  game = games_to_plot[k]
  # if (game %in% c('myAliens', 'avoidgeorge', 'survivezombies', 'zelda')){
  #   max_x=3000
  # }else{
  #   max_x = 1000
  # }

  max_x = 1000
  
  ## used for adding data points to sparse DDQN data
  if(max_x<5000){
    step_size=5
  }else if(max_x<100000){
    step_size=100
  }else if(max_x<1000000){
    step_size=1000
  }else{
    step_size=10000
  }
  
  d = filter(alldata, game_name==game, agent_type %in% agents_to_plot)
  ### assign correct colors to each subject ID
  plotcolors = c()
  for (agent in agents_to_plot){
    agent_subjects = unique(filter(d, agent_type==agent)$subject_ID)
    agent_color = colors[agent]
    colorlist = rep(agent_color, length(agent_subjects))
    names(colorlist) = agent_subjects
    plotcolors = c(plotcolors, colorlist)
  }
  
  if (game%in%levels(excluded_subjects)){
    es = filter(excluded_subjects, game_name==game)
    subjects_to_exclude = unique(es$subject_ID)
  }else{
    subjects_to_exclude = c()
  }

  d = filter(d, !(subject_ID%in%subjects_to_exclude))


  ## Add data points for every 'step_size' DDQN time-step, since we can afford to do this and know what the data points are
  ## (as we recorded end-of-episode data and cumulative_wins definitionally don't change before then)
  ## WARNING: if you ever plotted score, you wouldn't be able to do this. You didn't record score within episodes for DDQN.
  if (max_x<1000000){
  replacement_subjects = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
                              modelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
  for (subject in unique(filter(d, grepl('DDQN', agent_type))$subject_ID)){
    subject_data = filter(d, subject_ID==subject, cumulative_steps<max_x)
    
    ## if we actually have subject data for the max_x cutoff we care about...
    if (length(subject_data$cumulative_steps)>0){
      subject_agent_type = subject_data$agent_type[1]
      last_steps = 0
      
      new_subject_df = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
                                  modelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
      
      for (i in 1:length(subject_data$cumulative_steps)){ ## meaning, for each episode
        subject_row = subject_data[i,]
        if (last_steps<subject_row$cumulative_steps){
        # for (j in last_steps:(subject_row$cumulative_steps-1)){
          for (j in seq(last_steps, subject_row$cumulative_steps-1,step_size)){
                    row = data.frame(game_name=game, agent_type=subject_data$agent_type[1], long_agent_type=subject_data$long_agent_type[1], subject_ID=subject,
                           modelrun_ID=subject_data$modelrun_ID[1], level_number=subject_row$level_number, cumulative_steps=j, cumulative_wins=subject_row$cumulative_wins,
                           score=subject_row$score)
          new_subject_df = rbind(new_subject_df, row)
        }
        new_subject_df = rbind(new_subject_df, subject_row)
        last_steps = subject_row$cumulative_steps
      }
      }
      replacement_subjects = rbind(replacement_subjects, new_subject_df)
    } 
    
    d=filter(d, !grepl('DDQN', agent_type))
    d = rbind(d, replacement_subjects) 
    }
  }
  
  d = filter(d, cumulative_steps<=max_x)
  
  ## you can only assume DDQN kept playing for max_x steps. Humans might have quit before then, and EMPA might be stuck thinking, within the allotted limit.
  no_win_subjects = c()
  for (subject in unique(d$subject_ID)){
    if (max(filter(d, subject_ID==subject, cumulative_steps<=max_x)$cumulative_wins)==0){
      no_win_subjects = c(no_win_subjects, subject)
    }
  }
  
  ### calculate kappas here:
  kappa_df = data.frame(agent_type=as.character, efficiency=as.numeric())
  for (agent in unique(d$agent_type)){
    agent_data = filter(d, agent_type==agent)
    
    level_maxes = list()
    cumulative_step_maxes = list()
    idx=1
    for (l in 1:length(unique(agent_data$subject_ID))){
      subject = unique(agent_data$subject_ID)[l]
      subjectdata = filter(agent_data, subject_ID==subject)
      if (length(subjectdata$cumulative_steps)>0){
        if(max(subjectdata$cumulative_steps)>0){
          level_maxes[[idx]] = max(subjectdata$cumulative_wins)
          cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
          idx = idx+1            
        }
      }
    }
    
    ## mean vector of win numbers
    mean_wins = mean(as.numeric(as.vector(level_maxes)))
    
    ##mean of vector steps+to+win ratios (kappa)
    l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
    kappa_df = rbind(kappa_df, data.frame(agent_type=agent, efficiency=l_e))
  }
  
  ## round kappa just to exponents
  ## do you put kappa in a box, or do you do this manually?
  # kappa_df$formatted_efficiency = formatC(kappa_df$efficiency, format = "e", digits = 0)
  # for (o in 1:length(kappa_df$formatted_efficiency)){
  #  if(kappa_df$formatted_efficiency[o]=='0e+00'){
  #    kappa_df$formatted_efficiency[o] = '0.0'
  #  }
  #    kappa_df$formatted_efficiency[o] = sub('e-0','e-',kappa_df$formatted_efficiency[o])
  # }
  
  
  d=transform(d, subject_ID=factor(subject_ID, levels=names(plotcolors))) ## reorder in order to plot EMPA on top, as it otherwise can get lost in the many human curves.
  max_y = max(d$cumulative_wins)
  
  game_title=gsub('_',' ',game)
  if (game_title=='ee'){
    game_title='explore/exploit'
  }
  if (game_title=='ee 1'){
    game_title='explore/exploit 1'
  }
  if (game_title=='ee 2'){
    game_title='explore/exploit 2'
  }
  if (game_title=='ee 3'){
    game_title='explore/exploit 3'
  }
  p = ggplot(d ,aes(x=cumulative_steps,y=cumulative_wins, color=subject_ID, size=agent_type))+geom_point()+ 
    ggtitle(game_title)+theme(legend.position="none")+scale_color_manual(values=plotcolors)+scale_size_manual(values=c(1,1,1))+
    xlab('Steps taken by agent')+ylab('Levels won')+
    theme(plot.title=element_text(family='',face='plain', size=26),
          axis.text.x=element_text(size=22),
          axis.text.y=element_text(size=22),
          axis.title.x=element_text(size=24),
          axis.title.y=element_text(size=24))
  
  p=p+geom_smooth(data=filter(d,!(subject_ID%in%no_win_subjects)), se=FALSE)
  if ( (length(no_win_subjects)>0) & length(filter(d,subject_ID%in%no_win_subjects,grepl('DDQN', agent_type))$cumulative_steps>0) ){
    p = p+geom_segment(aes(x=0,y=0,xend=max_x,yend=0),data=filter(d,subject_ID%in%no_win_subjects,grepl('DDQN', agent_type)),size=1.4)
  }
  ## there are some games where you got 0 DDQN data in short ranges of time, like 1k steps for chase.
  if (length(filter(d, grepl('DDQN', agent_type), cumulative_steps<max_x)$cumulative_steps)==0){
    p = p+geom_segment(aes(x=0,y=0,xend=max_x,yend=0),data=d,size=1.4, color=colors['DDQN 100k'])
  }
  
  p=p+xlim(0,max_x)+ylim(0,max_y)
  
  if(max_x==1000000){
    p=p+scale_x_continuous(breaks=c(0, 250000, 500000, 750000, 1000000),labels=c('0', '250k', '500k', '750k', '1mil'), limits=c(0,1000000))
  }

  human_kappa = filter(kappa_df, agent_type=='human')$formatted_efficiency
  EMPA_kappa = filter(kappa_df, agent_type=='EMPA')$formatted_efficiency
  DDQN_kappa = filter(kappa_df, agent_type=='DDQN 100k')$formatted_efficiency
  kappa_string = paste('Learning efficiency (\u03ba):','\nHuman: ', human_kappa, '\nEMPA: ', 
                       EMPA_kappa, '\nDDQN: ', 
                       DDQN_kappa, sep='')

  # p=p+annotate("label", x = max_x*.75, y = max_y*.6, label = kappa_string, size=7)
  
  p=p+annotate("label", x = max_x*.25, y = max_y*.6, label = kappa_string, size=7)

  ## Can get different colors, but if you build up the plot line by line, you won't get automatic centering.
  # p+annotate("text",x=max_x*.75, y=3, hjust = 0, parse=T, label='"Learning efficiency (\u03ba):"', color="black") +
    # annotate("text", x =  max_x*.75, y=2.8, hjust = 0, parse=T, label='"Pontiac Firebird"', color="green")
  
  print(length(plots))
  plots[[k]] = p
  
  newdir=paste('~/Projects/atari/vgdl/plots/learning_curves/max=', max_x/1000, 'k/', sep='')
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=8, height=6)
}

## plots_1k_with_box, plots_10k_with_box, plots_100k_with_box, plots_1mil_with_box
## multi_1k_with_box, multi_10k_with_box, multi_1mil_with_box
plots_1k = plots
plots_10k = plots
plots_100k = plots
plots_1mil = plots

layout = matrix(c(1:90), ncol=6, byrow=TRUE)
m = multiplot(plotlist = plots_1mil, layout=layout)

multi_1k = m
multi_10k = m
multi_100k =m
multi_1mil = m
multi_1mil_with_box = m
## save 50x30


## levels won plot
ordered_agents = data.frame(agent_type=as.character(), mean_levels_won=as.numeric())
for (agent in unique(filter(human_normed_data, agent_type!='random policy')$agent_type)){
  ordered_agents = rbind(ordered_agents, data.frame(agent_type=agent, mean_levels_won=mean(filter(human_normed_data, agent_type==agent)$mean_levels_won)))
}
ordered_agents
ordered_names = ordered_agents[order(ordered_agents$mean_levels_won, decreasing=TRUE),]$agent_type

p = ggplot(filter(human_normed_data, agent_type!='random policy'), aes(agent_type, y=mean_levels_won, fill=agent_type))+geom_bar(stat='summary', fun.y='mean')+scale_fill_manual(values=colors)+
  scale_x_discrete(limits=ordered_names)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab('Mean levels won')
p


human_normed_data$formatted_game_name = NA
for (i in 1:length(human_normed_data$game_name)){
  human_normed_data$formatted_game_name[i] = gsub('_', ' ', human_normed_data$game_name[i])
  if (human_normed_data$formatted_game_name[i]=='ee'){
    human_normed_data$formatted_game_name[i] = 'explore/exploit'
  }
  if (human_normed_data$formatted_game_name[i]=='ee 1'){
    human_normed_data$formatted_game_name[i] = 'explore/exploit 1'
  }
  if (human_normed_data$formatted_game_name[i]=='ee 2'){
    human_normed_data$formatted_game_name[i] = 'explore/exploit 2'
  }
  if (human_normed_data$formatted_game_name[i]=='ee 3'){
    human_normed_data$formatted_game_name[i] = 'explore/exploit 3'
  }
}

#### MAIN FIGURE ###
main_plot_agent_types = c('DDQN 100k', 'EMPA')
s = filter(human_normed_data, agent_type=='EMPA')
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$formatted_game_name
p = ggplot()+
  geom_bar(data=filter(human_normed_data, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(human_normed_composite_ratio, 10)>-3),
           aes(x=formatted_game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_point(data=filter(human_normed_data, agent_type%in%main_plot_agent_types & ((agent_type != 'DDQN 100k'  & !(log(human_normed_composite_ratio, 10)>-3)) | agent_type=='DDQN 100k')),
             aes(x=formatted_game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  # theme(legend.position="none")+
  colorScale+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),legend.position='none')+ylab("Human-normed Efficiency")+xlab('Game name')+ylim(-10,10)
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p + scale_fill_manual(values=colors,name="Model",
                      breaks=c("EMPA", "DDQN 100k"),
                      labels=c("EMPA", "DDQN")) + scale_color_manual(values=colors,name="Model",
                                                                                         breaks=c("EMPA", "DDQN 100k"),
                                                                                         labels=c("EMPA", "DDQN"))
## 14x10


## density plot summary plot of overall results -- easy to look at.
# (agent_type%in%c('EMPA','no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW', 'no subgoals + no gradient + no IW')
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (failure)',10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)

# human_normed_data = transform(human_normed_data, agent_type=factor(agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 
#                                                                                      'no goal gradient', 'no subgoals',  'no subgoals + no gradient',
#                                                                                      'no IW', 'no subgoals + no gradient + no IW',
#                                                                                      'DDQN 1k', 'DDQN 10k', 'DDQN 100k', 'random policy')))
human_normed_data = transform(human_normed_data, agent_type=factor(agent_type, levels=c('human', 'EMPA',
                                                                                        'e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k',
                                                                                        'no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                                                                                        'no IW', 'no subgoals + no gradient + no IW',
                                                                                        'DDQN 1k', 'DDQN 10k', 'DDQN 100k', 
                                                                                        'rainbow 250k', 'rainbow 150k', 'rainbow 50k',
                                                                                        'random policy')))
human_normed_data$model_cluster = 'none'
human_normed_data[human_normed_data$agent_type=='EMPA',]$model_cluster = 'EMPA'
human_normed_data[human_normed_data$agent_type%in%c('e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k'),]$model_cluster = 'Exploration ablations'
human_normed_data[human_normed_data$agent_type%in%c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                                                    'no IW', 'no subgoals + no gradient + no IW'),]$model_cluster = 'Planner ablations'
human_normed_data[human_normed_data$agent_type%in%c('DDQN 1k', 'DDQN 10k', 'DDQN 100k'),]$model_cluster = 'DDQN'
human_normed_data[human_normed_data$agent_type%in%c('rainbow 50k', 'rainbow 150k', 'rainbow 250k'),]$model_cluster = 'rainbow'

human_normed_data = transform(human_normed_data, model_cluster=factor(model_cluster, levels=c('EMPA', 'Exploration ablations', 'Planner ablations', 'DDQN', 'rainbow', NA)))

# human_normed_data = transform(human_normed_data, model_cluster=factor(model_cluster, levels=c('EMPA', 'exploration lesions', 'DDQN', NA)))

### Stacked plot; each model type gets one row
# p = ggplot(filter(human_normed_data, !agent_type%in%c('human', 'random policy')), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
#   geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
#   scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed Efficiency") + ylab("Density") + 
#   geom_vline(xintercept=0,linetype='dashed',size=.4)+facet_wrap(~agent_type, ncol=1)
# p # 12x10
# 
# ### Stacked and organized by lesion type
# p = ggplot(filter(human_normed_data, !agent_type%in%c('human', 'random policy')), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
#   geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+geom_boxplot(aes(x=log(human_normed_composite_ratio), y=.75))+
#   scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed Efficiency") + ylab("Density") + 
#   geom_vline(xintercept=0,linetype='dashed',size=.4)+facet_wrap(~model_cluster, ncol=1)
# p # 8x10
# 
# 
# p = ggplot(filter(human_normed_data, agent_type%in%c('EMPA')))+
#   geom_boxplot(aes(x=agent_type, y=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+coord_flip()
# p  


## Facet-wrapped plot that shows quartiles!
# agents = c('EMPA', 'e-greedy .1', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k', 'no goal gradient', 'no subgoals + no gradient', 'no IW', 'no subgoals', 'no subgoals + no gradient + no IW')
agents = c('EMPA', 'e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k', 'rainbow 250k', 'rainbow 150k', 'rainbow 50k', 'no goal gradient', 'no subgoals + no gradient', 'no IW', 'no subgoals', 'no subgoals + no gradient + no IW')
datapoints = data.frame(x1=as.numeric(), x2=as.numeric(), x3=as.numeric(), x4=as.numeric(), x5=as.numeric(), 
                        y1=as.numeric(), y2=as.numeric(), y3=as.numeric(), mean_val=as.numeric(), agent_type=as.character(), model_cluster=as.character())
for (i in 1:length(agents)){
  agent = agents[i]
  ## Trying to just add the boxplot data manually
  quantiles = quantile(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio), c(.1, .25, .5, .75, .9))
  mn=mean(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio))
  # q1=quantiles[2]
  # q2=quantiles[3]
  # q3=quantiles[4]
  q1=quantiles[1]
  q2=quantiles[2]
  q3=quantiles[3]
  q4=quantiles[4]
  q5=quantiles[5]
  if (agent == 'EMPA'){
    m_cluster = 'EMPA'
  }
  if (agent %in% c('e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k')){
    m_cluster = 'Exploration ablations'
  }
  if (agent%in% c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                  'no IW', 'no subgoals + no gradient + no IW')){
    m_cluster = 'Planner ablations'
  }
  if (agent %in% c('DDQN 1k', 'DDQN 10k', 'DDQN 100k')){
      m_cluster = 'DDQN'
  }
  if(grepl('rainbow', agent)){
    m_cluster = 'rainbow'
  }
  
  
  # y1=1.06
  # y2=1.1
  # y3=1.14
  y1=.875
  y2=.9
  y3=.925
  ## offsets for planner lesions
  if(agent=='no subgoals'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='no subgoals + no gradient'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  if(agent=='no IW'){
    y1 = y1-.18
    y2 = y2-.18
    y3 = y3-.18
  }
  if(agent=='no subgoals + no gradient + no IW'){
    y1 = y1-.24
    y2 = y2-.24
    y3 = y3-.24
  }
  
  ## offsets for exploration lesions
  if(agent=='e-greedy 1k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='e-greedy 2k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  if(agent=='e-greedy 1k DS'){
    y1 = y1-.18
    y2 = y2-.18
    y3 = y3-.18
  }
  if(agent=='e-greedy 2k DS'){
    y1 = y1-.24
    y2 = y2-.24
    y3 = y3-.24
  }
  
  ##offsets for DDQN
  if(agent=='DDQN 10k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='DDQN 100k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  
  ##offsets for rainbow
  if(agent=='rainbow 150k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='rainbow 250k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  
  # datapoints = rbind(datapoints, data.frame(x1=q1, x2=q2, x3=q3, y1=y1, y2=y2, y3=y3,agent_type=agent,model_cluster=m_cluster))
  
  datapoints = rbind(datapoints, data.frame(x1=q1, x2=q2, x3=q3, x4=q4, x5=q5,y1=y1, y2=y2, y3=y3, mean_val=mn, agent_type=agent,model_cluster=m_cluster))
  }

colors = c('steelblue1', #EMPA
           # 'purple1', 'purple2', 'purple3', 'purple4', #e-greedy
           # 'orchid1','mediumorchid1', 'mediumpurple1', 'purple1',
           'slateblue1', 'slateblue4', 'mediumpurple1', 'purple1',
           
          # 'slateblue1', 'slateblue3', 'purple1', 'purple3',
           # 'royalblue1', 'royalblue3', 'purple1', 'purple3',
           # 'royalblue1', 'dodgerblue1', 'purple1', 'slateblue1',
           # 'royalblue1', 'blue1', 'purple1', 'slateblue1',
           
                      'firebrick2',# 'seagreen3','darkolivegreen1',
           'palegreen3',
           # 'gray50', 'gray52', 'gray54',
           'gray50', 'gray65', 'gray80',
          # 'tomato1', 'tomato3', 'salmon', 
           'orange3', 'tomato3', 'red3', 
          
                                'goldenrod1', 'goldenrod2', 'goldenrod3', 'darkslategray2', 'darkolivegreen3')
names(colors)=c('EMPA', 
                'e-greedy 1k', 'e-greedy 2k', 'e-greedy 1k DS', 'e-greedy 2k DS',
                'random policy',
                'human',
                'DDQN 100k', 'DDQN 10k', 'DDQN 1k',
                'rainbow 250k', 'rainbow 150k', 'rainbow 50k',
                'no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW', 'no subgoals + no gradient + no IW')


#### aug 4: to plot everything, incl. ablations
df = filter(human_normed_data, agent%in%agents, !is.na(model_cluster))
df = transform(df, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy 1k', 'e-greedy 2k', 'e-greedy 1k DS', 'e-greedy 2k DS',
                                                          'no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW',
                                                          'no subgoals + no gradient + no IW', 'DDQN 1k', 'DDQN 10k', 'DDQN 100k',
                                                          'rainbow 250k', 'rainbow 150k', 'rainbow 50k')))

## to plot just empa ddqn rainbow
rainbow_games = unique(filter(human_normed_data, model_cluster=='rainbow')$game_name)
df = filter(human_normed_data, agent%in%agents, model_cluster%in%c('EMPA', 'DDQN', 'rainbow'), game_name%in%rainbow_games) ##to plot just empa ddqn rainbow
df = transform(df, agent_type=factor(agent_type, levels=c("human", "EMPA",
                                                                     'DDQN 1k', 'DDQN 10k', 'DDQN 100k',
                                                                      'rainbow 250k', 'rainbow 150k', 'rainbow 50k')))
df = transform(df, model_cluster=factor(model_cluster, levels=c('EMPA','DDQN','rainbow')))
datapoints = filter(datapoints, model_cluster%in%c('EMPA', 'DDQN', 'rainbow'))

tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)',10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
p = ggplot(df, aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed Efficiency") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.8)+ ## originally .4

  # geom_segment(aes(x=x2, y=y2, xend=x4, yend=y2), data=datapoints)+
  # geom_segment(aes(x=x1, y=y1, xend=x1, yend=y3), data=datapoints)+
  # geom_segment(aes(x=x3, y=y1, xend=x3, yend=y3), data=datapoints)+
  # geom_segment(aes(x=x2, y=y1, xend=x2, yend=y3), data=datapoints)+
  geom_point(aes(x=mean_val, y=y2), shape=18, data=datapoints, size=7)+
  # geom_segment(aes(x=x1, y=y2, xend=x2, yend=y2), linetype='dotted', data=datapoints, size=2.4)+ ##5-25 ## pretty good
  geom_segment(aes(x=x1, y=y2, xend=x2, yend=y2), linetype='longdash', data=datapoints, size=1.2)+ ##5-25 ## pretty good
  
    geom_segment(aes(x=x2, y=y2, xend=x4, yend=y2), data=datapoints, size=1.2)+ ##25-75
  geom_segment(aes(x=x2, y=y1, xend=x2, yend=y3), data=datapoints, size=1.2)+ ##25 edge
  geom_segment(aes(x=x4, y=y1, xend=x4, yend=y3), data=datapoints, size=1.2)+ ## 75 edge
  # geom_segment(aes(x=x4, y=y2, xend=x5, yend=y2), linetype='dotted', data=datapoints, size=2.4)+ ##75-95
    geom_segment(aes(x=x4, y=y2, xend=x5, yend=y2), linetype='longdash', data=datapoints, size=1.2)+ ##75-95
  
  geom_segment(aes(x=x3, y=y1, xend=x3, yend=y3), data=datapoints, size=1.2)+ ##median line
  
      theme(legend.title=element_blank(), text=element_text(size=38), #legend.position='none',
            axis.text.x=element_text(size=34), axis.text.y=element_text(size=34), strip.text.x=element_text(size=44))+
  scale_x_continuous(breaks=logtickmarks,labels=tickmarks, limits=c(logtickmarks[1], 7.5)) +
  scale_y_continuous(limits=c(0,.95), breaks=c(0,.2,.4,.6,.8), labels=c(0,.2,.4,.6,.8))+
  facet_wrap(~model_cluster, ncol=1)
p
## 30x18


## attempt to produce individual plots with quartiles.
# plots = list()
# i=1
# agents = c('EMPA', 'e-greedy .1', 'DDQN 100k')
# for (i in 1:length(agents)){
#   agent = agents[i]
#   ## Trying to just add the boxplot data manually
#   quantiles = quantile(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio))
#   print(agent)
#   print (i)
# 
#   q1=quantiles[2]
#   q2=quantiles[3]
#   q3=quantiles[4]
#   datapoints = data.frame(x=c(q1,q3), y=c(1.2, 1.2), agent_type=agent)
#   print(datapoints)
#   p = ggplot(filter(human_normed_data, agent_type==agent), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
#     geom_density(alpha=.8, adjust= 1/10)+
#     scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed performance") + ylab("Density") + 
#     geom_vline(xintercept=0,linetype='dashed',size=.4)+
#     geom_segment(aes(x=datapoints[1,]$x, y=datapoints[1,]$y, xend=datapoints[2,]$x, yend=datapoints[2,]$y), size=2, data=datapoints)+
#     theme(legend.title=element_blank())+scale_x_continuous(breaks=logtickmarks,labels=tickmarks, limits=c(logtickmarks[1], 6))
#     #+facet_wrap(~model_cluster, ncol=1)
#   p
#   newdir='~/Projects/atari/vgdl/plots/densities/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, agent, '.png', sep='')
#   ggsave(title, plot=p, width=7, height=3)
#   # i = i+1
# }

# layout = matrix(c(1:length(plots)), nrow=length(plots))
# m = multiplot(plotlist = plots, layout=layout)
# 8x10

## one plot per game summary plot of overall results -- easy to look at.
p = ggplot(subset(human_normed_data), aes(x=agent_type, y=level_percentage, fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='identity')+facet_wrap(~game_name)+scale_fill_manual(values=colors)+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+theme(legend.position='bottom')
p
## save as 10x16


p = ggplot(agentdata, aes(x=cumulative_steps, y=cumulative_wins, color=subject_ID))+geom_point()+geom_smooth()
p

## looks like 10 subjects won zelda, the rest did far worse (0,1, or 2 levels). Be careful how you average.
### you first need to generate cumulative wins
###level1-level2 plots
level_win_saved = level_win
level_win_proportions = level_win
d = filter(alldata, agent_type%in%c('human', 'EMPA', 'DDQN 100k', 'e-greedy .1'))

make_level_win_data = function(d){
  level_win = data.frame(agent_type=as.character(), subject_ID=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$agent_type)){
      agentdata = filter(s, agent_type==agent)
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps - prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            subject_steps_to_win = level_steps
            # subject_steps_to_win = 1
          }
          else{
            subject_steps_to_win = no_win_equivalent_steps
            # subject_steps_to_win = 0
          }
          row = data.frame(agent_type=agent, subject_ID=subject, game_name=game, level_num=l, steps=subject_steps_to_win)
          level_win=rbind(level_win, row)
        }
      }
    }
  }
  level_win = transform(level_win, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy .1', "DDQN 100k"))) ## so that columns of plot are reordered
  return(level_win)
}


make_level_win_proportions = function(d){
  level_win = data.frame(agent_type=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$agent_type)){
      agentdata = filter(s, agent_type==agent)

      across_subjects = c()
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps - prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            # subject_steps_to_win = c(subject_steps_to_win, level_steps)
            subject_steps_to_win = c(subject_steps_to_win, 1)
          }
          else{
            # subject_steps_to_win = c(subject_steps_to_win, no_win_equivalent_steps)
            subject_steps_to_win = c(subject_steps_to_win, 0)

          }
        }
        across_subjects = rbind(across_subjects, subject_steps_to_win)
      }
      across_subjects  = colMeans(across_subjects)
      for (l in levels_to_try){
        row = data.frame(agent_type=agent, game_name=game, level_num=l, steps=across_subjects[l])
        level_win=rbind(level_win, row)

      }
    }
  }
  level_win = transform(level_win, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy .1', "DDQN 100k"))) ## so that columns of plot are reordered
  return(level_win)
}

level_win_proportions = make_level_win_proportions(d)

##Plot of steps to win level 1, conditioned on winning level 0. Only for games where the model *did* win level 1.
##Only the DDQN failed to win level 1
tmpcolors = c('palegreen3','steelblue3','slateblue2','grey50')
names(tmpcolors) = c('human', 'EMPA','e-greedy .1', 'DDQN 100k')

# p = ggplot(subset(level_win, level_num==1&steps!=-Inf), aes(x=short_agent_type, y=log(steps,10), fill=short_agent_type))
# p=p+geom_bar(position='dodge', stat='summary', fun.y='mean')+theme(legend.position='none')+scale_fill_manual(values=colors)
# p


# level_win_no_inf[level_win_no_inf$steps==10e15,]$steps=10e8

tickmarks = c(1,10e0,10e1,10e2,10e3,10e4,10e5,10e6,10e7,10e8,10e9,10e10,10e11,10e12,10e13,10e14,10e15)
logtickmarks=(log(tickmarks,10))

level_win = transform(level_win, agent_type=factor(agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k')))

## all levels
p = ggplot(level_win, aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+scale_color_manual(values=tmpcolors)+
  scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+facet_wrap(~level_num, ncol=1)
p


## levels 1, 2
p = ggplot(filter(level_win_old, level_num%in%c(1,2)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+scale_color_manual(values=tmpcolors)+
  scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+facet_wrap(~level_num, ncol=1)
p

## Individual plots for steps to level 1, steps to level 2...
p = ggplot(filter(level_win, level_num%in%c(1)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  
    scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_linetype_manual(values=c(1,2,3,4,5))
p

## Individual plots for steps to level 1, steps to level 2...
p = ggplot(filter(level_win,level_num%in%c(2)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==2)$steps,10), na.rm=TRUE), linetype='l'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==2)$steps,10), na.rm=TRUE), linetype='k'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==2)$steps,10), na.rm=TRUE), linetype='j'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==2)$steps,10), na.rm=TRUE), linetype='i'))+
  
  scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p

p = ggplot(filter(level_win,level_num%in%c(3)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==3)$steps,10), na.rm=TRUE), linetype='l'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==3)$steps,10), na.rm=TRUE), linetype='k'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==3)$steps,10), na.rm=TRUE), linetype='j'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==3)$steps,10), na.rm=TRUE), linetype='i'))+
  
  scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p



p = ggplot(level_win_proportions, aes(x=level_num, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='summary',fun.y='mean', position='dodge')+
  scale_fill_manual(values=tmpcolors)+facet_wrap(~agent_type, nrow=1)
p=p+ylab('Proportion')+ggtitle('Level completion across games')+xlab("Level number")
p


p = ggplot(level_win_proportions, aes(x=game_name, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='identity', position='dodge')+
  scale_fill_manual(values=tmpcolors)+facet_wrap(~level_num, ncol=1) #facet_grid(level_num~game_name)#
p=p+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab('Proportion of agents to complete level')
p


for (game in unique(level_win_proportions$game_name)){
  p = ggplot(filter(level_win_proportions, game_name==game), aes(x=agent_type, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='identity', position='dodge')+
    scale_fill_manual(values=tmpcolors)+facet_wrap(~level_num, ncol=1) #facet_grid(level_num~game_name)#
  p=p+ggtitle(game)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab('Proportion of agents to complete level')
  
  newdir='~/Projects/atari/vgdl/interaction_plots/agent_win_proportions/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=4, height=6)
  
}


# complete_games = c()
# overcomplete_games = c()
# for (game in unique(EMPA_data$game_name)){
#   l = length(unique(filter(EMPA_data, game_name==game)$subject_ID))
#   if (l!=10){
#     overcomplete_games = c(overcomplete_games, game)
#   }else{
#     complete_games = c(complete_games, game)
#   }
# }

# for (game in complete_games){
#   p = ggplot(filter(EMPA_data, game_name==game), aes(x=cumulative_timestep, y=cumulative_wins, color=subject_ID))
#   p = p+geom_point()+geom_smooth()
#   # p
#   newdir='~/Projects/atari/vgdl/empa_plots/by_subject/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, game, '.png', sep='')
#   ggsave(title, plot=p, width=7, height=5) 
# }

### Planner lesion plot

## Standard boxplots
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p = ggplot(filter(human_normed_data, model_cluster%in%c('EMPA', 'planner lesions'))) + 
  geom_boxplot(aes(x=agent_type, y=log(human_normed_composite_ratio), fill=agent_type), outlier.shape=NA)+ # outlier.shape=NA removes outliers
  scale_color_manual(values=colors)+scale_fill_manual(values=colors)+
  scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p

## Facet-wrapped plot that shows quartiles!
agents = c('EMPA', 'e-greedy .1', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k', 'no goal gradient', 'no subgoals + no gradient', 'no IW', 'no subgoals', 'no subgoals + no gradient + no IW')
boxplot_datapoints = data.frame(x1=as.numeric(), x2=as.numeric(), x3=as.numeric(), x4=as.numeric(), x5=as.numeric(), 
                        y1=as.numeric(), y2=as.numeric(), y3=as.numeric(), mean_val=as.numeric(), agent_type=as.character(), model_cluster=as.character())
for (i in 1:length(agents)){
  agent = agents[i]
  ## Trying to just add the boxplot data manually
  quantiles = quantile(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio), c(.1, .25, .5, .75, .9))
  mn=mean(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio))
  # q1=quantiles[2]
  # q2=quantiles[3]
  # q3=quantiles[4]
  q1=quantiles[1]
  q2=quantiles[2]
  q3=quantiles[3]
  q4=quantiles[4]
  q5=quantiles[5]
  if (agent == 'EMPA'){
    m_cluster = 'EMPA'
  }
  if (agent %in% c('e-greedy .1')){
    m_cluster = 'exploration lesions'
  }
  if (agent%in% c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                  'no IW', 'no subgoals + no gradient + no IW')){
    m_cluster = 'planner lesions'
  }
  if (agent %in% c('DDQN 1k', 'DDQN 10k', 'DDQN 100k')){
    m_cluster = 'DDQN'
  }
  
  y1=.9
  y2=1
  y3=1.1
  ## offsets for planner lesions
  if(agent=='no subgoals'){
    y1 = y1-.5
    y2 = y2-.5
    y3 = y3-.5
  }
    if(agent=='no goal gradient'){
    y1 = y1-1
    y2 = y2-1
    y3 = y3-1
  }
  if(agent=='no subgoals + no gradient'){
    y1 = y1-1.5
    y2 = y2-1.5
    y3 = y3-1.5
  }
  if(agent=='no IW'){
    y1 = y1-2
    y2 = y2-2
    y3 = y3-2
  }
  if(agent=='no subgoals + no gradient + no IW'){
    y1 = y1-2.5
    y2 = y2-2.5
    y3 = y3-2.5
  }
  
  ##add offsets for e-greedy before making plot

  ##offsets for DDQN
  if(agent=='DDQN 10k'){
    y1 = y1-3
    y2 = y2-3
    y3 = y3-3
  }
  if(agent=='DDQN 1k'){
    y1 = y1-3.5
    y2 = y2-3.5
    y3 = y3-3.5
  }
  
  boxplot_datapoints = rbind(boxplot_datapoints, data.frame(x1=q1, x2=q2, x3=q3, x4=q4, x5=q5,y1=y1, y2=y2, y3=y3, mean_val=mn, agent_type=agent,model_cluster=m_cluster))
}



data_to_plot = filter(boxplot_datapoints, model_cluster%in%c('EMPA', 'planner lesions'))
p = ggplot(data_to_plot, aes(color=agent_type)) + 
  geom_segment(aes(x=y2,y=x1,xend=y2,yend=x2), data=data_to_plot, linetype='dashed')+ ##10-25
  geom_segment(aes(x=y2,y=x4,xend=y2,yend=x5), data=data_to_plot, linetype='dashed')+ ##75-90
  
    # geom_segment(aes(x=y2,y=x2,xend=y2,yend=x4), data=data_to_plot)+ ##25+75. just use this is you want a single line 
  geom_segment(aes(x=y1,y=x2,xend=y1,yend=x4), data=data_to_plot)+ ##25+75. vertical edge
  geom_segment(aes(x=y3,y=x2,xend=y3,yend=x4), data=data_to_plot)+ ##25+75. vertical edge
  geom_segment(aes(x=y1,y=x2,xend=y3,yend=x2), data=data_to_plot)+ ##25+75. horizontal edge
  geom_segment(aes(x=y1,y=x4,xend=y3,yend=x4), data=data_to_plot)+ ##25+75. horizontal edge
  geom_point(aes(y=mean_val, x=y2), shape=5, data=data_to_plot)+ ##mean
  geom_segment(aes(x=y1,y=x3,xend=y3,yend=x3), data=data_to_plot)+
  scale_y_continuous(breaks=logtickmarks,labels=tickmarks)+
  ylab('Human-normed composite ratio')+xlab('Agent type')+ theme(axis.text.x = element_blank(), axis.ticks = element_blank())+
  scale_color_manual(values=colors)
p



eg = filter(alldata, agent_type=='e+greedy .1')
df = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(), level_number=as.numeric(),
                cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric(), subsample_ID=as.character())
for (i in 1:10){
  tmp_df = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(), level_number=as.numeric(),
                  cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
  subjects_to_sample = sample(unique(eg$subject_ID), 3, replace = FALSE, prob = NULL)
  subsample = filter(eg, subject_ID%in%subjects_to_sample)
  tmp_df = rbind(tmp_df, subsample)
  tmp_df$subsample_ID = i
  df = rbind(df, tmp_df)
}


make_level_win_for_subsamples = function(d){
  lw = data.frame(subsample_ID=as.character(), subject_ID=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$subsample_ID)){
      agentdata = filter(s, subsample_ID==agent)
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps + prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            subject_steps_to_win = level_steps
            # subject_steps_to_win = 1
          }
          else{
            subject_steps_to_win = no_win_equivalent_steps
            # subject_steps_to_win = 0
          }
          row = data.frame(subsample_ID=agent, subject_ID=subject, game_name=game, level_num=l, steps=subject_steps_to_win)
          lw=rbind(lw, row)
        }
      }
    }
  }
  return(lw)
}
lw=make_level_win_for_subsamples(df)
head(lw)

lw$subsample_ID=as.factor(lw$subsample_ID)
p = ggplot(filter(lw,level_num%in%c(1)), aes(x=log(steps,10), color=subsample_ID, fill=subsample_ID))
p = p+geom_density(alpha=.8, adjust=1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p

### You should actually make a plantimeata figure if what you're trying to check is what e+greedy would look like there if not sampled enough times.

human_df=filter(alldata, agent_type=='human')
head(human_df)
df$agent_type=df$subsample_ID
df = select(df, +subsample_ID)
df=rbind(df, human_df)
human_normed_df = make_human_normed_data(df)

           
make_human_normed_data = function(dataframe){
  ## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
  plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                            max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                            level_num=as.numeric(), level_efficiency=as.numeric())
  
  for (j in 1:length(unique(dataframe$agent_type))){
    agent = unique(dataframe$agent_type)[j]
    print(agent)
    for (i in 1:length(unique(dataframe$game_name))){
      g = subset(dataframe, game_name==unique(dataframe$game_name)[i])
      print(unique(dataframe$game_name)[i])
      s = subset(g, agent_type==agent)
      if (length(s$cumulative_steps)>0){
        ## grab each subject's max_steps and max_wins.
        level_maxes = list()
        cumulative_step_maxes = list()
        idx=1
        for (k in 1:length(unique(s$subject_ID))){
          subject = unique(s$subject_ID)[k]
          subjectdata = s[which(s$subject_ID==subject),]
          if (length(subjectdata$cumulative_steps)>0){
            if(max(subjectdata$cumulative_steps)>0){
              level_maxes[[idx]] = max(subjectdata$cumulative_wins)
              cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
              idx = idx+1            
            }
            
          }
        }
        
        ## mean vector of win numbers
        mean_wins = mean(as.numeric(as.vector(level_maxes)))
        
        ##mean of vector steps+to+win ratios
        l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
        
        ## the row we want
        r = subset(s, cumulative_steps==max(cumulative_steps))[1,]
        ## take only the relevant columns and put them in the new data frame
        new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
                         max_steps=r$cumulative_steps, mean_levels_won=mean_wins,
                         level_num=subset(games_to_levels, (game_name==r$game_name))$num_levels,
                         level_efficiency=l_e)
        plantimedata = rbind(plantimedata, new)
      }
    }
  }
  
  
  plantimedata = mutate(plantimedata, level_percentage=mean_levels_won/level_num)
  plantimedata = mutate(plantimedata, composite_ratio = level_percentage*level_efficiency)
  
  plantimedata$human_normed_composite_ratio=NA
  ##norm by human level_efficiency
  for (i in 1:length(unique(plantimedata$game_name))){
    game = unique(plantimedata$game_name)[i]
    human_composite_ratio = subset(plantimedata, agent_type=='human' & game_name==game)$composite_ratio
    for (agent in unique(plantimedata$agent_type)){
      row = plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]
      plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]$human_normed_composite_ratio = row$composite_ratio/human_composite_ratio
    }
  }
  
  for (i in 1:length(plantimedata$human_normed_composite_ratio)){
    if (plantimedata$human_normed_composite_ratio[i]==0){
      plantimedata$human_normed_composite_ratio[i]=10e-8
    }
  }
  return(plantimedata)
  }

load_reward_data = function(data_to_load, dates_or_groups){
    if (data_to_load=='EMPA'){
      data = c()
      for (date in dates_or_groups){
      path = paste('~/Projects/atari/vgdl/',date, '/csv_data/merged_data', sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      
      # if ('exploration_burn_ins' %in% names(d)){
      #   d$exploration_burn_ins = as.numeric(d$exploration_burn_ins) ## you might want to make this as.numeric()
      # }else{
      #   d$exploration_burn_ins = NA
      # }
      
      if(length(data)==0){
        data = d
      }
      else{
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
        data = rbind(data,d)
      }
      }
      data$modelrun_ID = as.factor(data$modelrun_ID)
      data$cumulative_steps = as.numeric(as.character(data$cumulative_timestep))
      data$long_agent_type = as.factor(data$agent_type)
      
      newdata = data.frame()
      
      ## remove batchIDs so you can use grepl easily in the next part
      for (agent in unique(data$agent_type)){
        agent_data = filter(data, agent_type==agent)
        loc = regexpr('_batchID',agent)[1]
        if (loc>0){
          new_agent_type = substr(agent, 0, loc-1)
          agent_data$long_agent_type = new_agent_type
          agent_data$agent_type = new_agent_type
        }
        newdata = rbind(newdata, agent_data)
      }
      data = newdata
      
      
      ### e-greedy ones are poorly named?
      ## You ran 2k N on apr 4
      ## and you have 2k DS here
      
      ##
      
      e_greedy_05='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_1a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_1a1='rand=False_eG=True_egv=N_fe=0.1_sTE=1000'
      e_greedy_1b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_2a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_fe=0.1_sTE=1000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_2a1='rand=False_eG=True_egv=DSDF_fe=0.1_sTE=1000'
      e_greedy_2b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_fe=0.1_sTE=2000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_2b1='rand=False_eG=True_egv=DSDF_fe=0.1_sTE=2000'
      planner_AGH1a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH1_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH1b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH1_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH1c='eG=False_PL=AGH1'
      planner_AGH2a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH2_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH2b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH2_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH2c='eG=False_PL=AGH2'
      planner_AGH3a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH3b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH3_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH3c='eG=False_PL=AGH3'
      planner_IWa='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_IWb='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_IWc='eG=False_PL=IW'
      planner_IW_AGH3a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW+AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_IW_AGH3b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW-AGH3_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_IW_AGH3c='eG=False_PL=IW-AGH3'
      
      IW2_e_greedy_1='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      IW2_e_greedy_2='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      IW2_e_greedy_3='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_sTE=1000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      IW2_e_greedy_4='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_sTE=2000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      
      data$agent_type = NA
      if (e_greedy_1a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1a,]$agent_type = 'e-greedy 1k'
      }
      if (e_greedy_1b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1b,]$agent_type = 'e-greedy 2k'
      }
      if (e_greedy_2a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_2a,]$agent_type = 'e-greedy 1k DS'
      }
      if (e_greedy_2b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_2b,]$agent_type = 'e-greedy 2k DS'
      }
      if (e_greedy_05 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_05,]$agent_type = 'e-greedy .05'
      }
      if (planner_AGH1a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH1a,]$agent_type = 'no goal gradient'
      }
      if (planner_AGH2a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH2a,]$agent_type = 'no subgoals'
      }
      if (planner_AGH3a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH3a,]$agent_type = 'no subgoals + no gradient'
      }
      if (planner_IWa %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IWa,]$agent_type = 'no IW'
      }
      if (planner_IW_AGH3a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IW_AGH3a,]$agent_type = 'no subgoals + no gradient + no IW'
      }

      ## longer newer planner IDs:
      if (planner_AGH1b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH1b,]$agent_type = 'no goal gradient'
      }
      if (planner_AGH2b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH2b,]$agent_type = 'no subgoals'
      }
      if (planner_AGH3b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH3b,]$agent_type = 'no subgoals + no gradient'
      }
      if (planner_IWb %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IWb,]$agent_type = 'no IW'
      }
      if (planner_IW_AGH3b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IW_AGH3b,]$agent_type = 'no subgoals + no gradient + no IW'
      }
      
      ## shortest, newest planner IDs
      if (e_greedy_1a1 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1a1,]$agent_type = 'e-greedy 1k'
      }
      if (e_greedy_2a1 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_2a1,]$agent_type = 'e-greedy 1k DS'
      }
      if (e_greedy_2b1 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_2b1,]$agent_type = 'e-greedy 2k DS'
      }
      if ('rand=False_eG=False_egv=SS_fe=0.1_sTE=1000' %in% unique(data$long_agent_type)){
        data[data$long_agent_type=='rand=False_eG=False_egv=SS_fe=0.1_sTE=1000',]$agent_type = 'e-greedy 1k SS'
      }
      if ('rand=False_eG=False_egv=SN_fe=0.1_sTE=1000' %in% unique(data$long_agent_type)){
        data[data$long_agent_type=='rand=False_eG=False_egv=SN_fe=0.1_sTE=1000',]$agent_type = 'e-greedy 1k SN'
      }
      if (planner_AGH1c %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH1c,]$agent_type = 'no goal gradient'
      }
      if (planner_AGH2c %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH2c,]$agent_type = 'no subgoals'
      }
      if (planner_AGH3c %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH3c,]$agent_type = 'no subgoals + no gradient'
      }
      if (planner_IWc %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IWc,]$agent_type = 'no IW'
      }
      if (planner_IW_AGH3c %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IW_AGH3c,]$agent_type = 'no subgoals + no gradient + no IW'
      }
      ## old IW models we don't want
      if (IW2_e_greedy_1 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==IW2_e_greedy_1,]$agent_type = 'IW2 e-greedy. IGNORE.'
      }
      if (IW2_e_greedy_2 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==IW2_e_greedy_2,]$agent_type = 'IW2 e-greedy. IGNORE.'
      }
      if (IW2_e_greedy_3 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==IW2_e_greedy_3,]$agent_type = 'IW2 e-greedy. IGNORE.'
      }
      if (IW2_e_greedy_4 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==IW2_e_greedy_4,]$agent_type = 'IW2 e-greedy. IGNORE.'
      }
      for (agent in unique(data$long_agent_type)){
        if (grepl('rand=True', agent)){
          data[grepl('rand=True', data$long_agent_type),]$agent_type = 'random policy'
        }
      }
      if (NA %in% unique(data$agent_type)){
        data[is.na(data$agent_type),]$agent_type = 'EMPA'
      }
      
      data$score = as.numeric(as.character(data$sparse_score))
      data = select(data, -timestep, -level_max_score, -cumulative_max_score, -sparse_score, -level_accumulated_score, 
                    -episode_end, -win, -planner_nodes, -planner_settings, -cumulative_planner_nodes, 
                    -cumulative_timestep, condition, -exploration_burn_ins)
      if ('entropy'%in% names(data)){
        data = select(data, -entropy)
      }
      if ('time_elapsed'%in%names(data)){
        data = select(data, -time_elapsed)
      }
      if ('sparse_levels_won'%in%names(data)){
        data = select(data, -sparse_levels_won)
      }
      data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }else if (data_to_load == 'DDQN'){
    dqndata = list()
    for (gamefile in list.files(dqn_path)){
      filename = paste(dqn_path,gamefile,sep='')
      if(grepl('dqn/', filename)){
        gamenamestart = unlist(gregexpr('dqn/',filename))+nchar('dqn/')
        gamenameend = unlist(gregexpr('_reward', filename))+1        
      }else if (grepl('dqn_data/', filename)){
        gamenamestart = unlist(gregexpr('dqn_data/',filename))+nchar('dqn_data/')
        gamenameend = unlist(gregexpr('_DDQN_reward', filename))+1  
      }

      game = substr(filename, gamenamestart, gamenameend)
      if (grepl('k_', filename)){
        subject_ID_start = unlist(gregexpr('k_',filename))+2
        subject_ID_end = unlist(gregexpr('.csv', filename))+1
        subject_ID = substr(filename, subject_ID_start, subject_ID_end)
      }else{
        subject_ID = create_rand_string()
      }
      d=read.csv(filename, header=TRUE, na.strings='NA')
      
      d$score = d$ep_reward
      d$game_name = as.factor(remove_string_from_name(game))
      d$cumulative_steps = d$steps
      d$subject_ID = as.factor(subject_ID)
      
      if ((grepl('101', filename) || grepl('trial1', filename) || grepl('decay1k', filename))){
        d$agent_type = as.factor("DDQN 1k") ## refers to the eps_decay (epsilon-greedy annealing) parameter in the DDQN implementation. 
      }else if ((grepl('102', filename)|| grepl('trial2', filename) || grepl('decay10k', filename))){
        d$agent_type = as.factor("DDQN 10k")
      }else if ((grepl('103', filename)||grepl('trial3', filename) || grepl('decay100k', filename))){
        d$agent_type = as.factor("DDQN 100k")
      }else{
        d$agent_type = as.factor("DDQN")
      }
      d$long_agent_type = d$agent_type
      d$cumulative_wins = as.numeric(0)
      for (i in 2:length(d$level)){
        if (d$level[i]>d$level[i-1]){
          d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
          # d$sparse_levels_won[i] = d$cumulative_wins[i]
        }
        else{
          d$cumulative_wins[i] = d$cumulative_wins[i-1]
        }
      }
      d$level_number = d$level
      
      dqndata = rbind(dqndata,d)
    }
    data = dqndata
    data$modelrun_ID = NA
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
    
  }else if (data_to_load == 'rainbow'){
    rainbowdata = list()
    for (gamefile in list.files(rainbow_path)){
      filename = paste(rainbow_path,gamefile,sep='')
      if(grepl('rainbow/', filename)){
        gamenamestart = unlist(gregexpr('rainbow/',filename))+nchar('rainbow/')
        gamenameend = unlist(gregexpr('_reward', filename))+1        
      }else if (grepl('rainbow_data/', filename)){
        gamenamestart = unlist(gregexpr('rainbow_data/',filename))+nchar('rainbow_data/')
        gamenameend = unlist(gregexpr('_reward', filename))-1
      }
      
      game = substr(filename, gamenamestart, gamenameend)
      if (grepl('k_', filename)){
        subject_ID_start = unlist(gregexpr('k_',filename))+2
        subject_ID_end = unlist(gregexpr('.csv', filename))+1
        subject_ID = substr(filename, subject_ID_start, subject_ID_end)
      }else{
        subject_ID = create_rand_string()
      }
      d=read.csv(filename, header=TRUE, na.strings='NA')
      
      d$score = d$ep_reward
      d$game_name = as.factor(remove_string_from_name(game))
      d$cumulative_steps = d$steps
      d$subject_ID = as.factor(subject_ID)
      
      ## WARNING: This is not robust to ordering trial numbers differently.
      if (grepl('trial10', filename)){
        d$agent_type = as.factor("rainbow 50k") ## refers to the eps_decay (epsilon-greedy annealing) parameter in the DDQN implementation. 
      }else if (grepl('trial1', filename)){
        d$agent_type = as.factor("rainbow 250k")
      }else if (grepl('trial23', filename)){
        d$agent_type = as.factor("rainbow 150k")
      }else{
        d$agent_type = as.factor("rainbow")
      }
      d$long_agent_type = d$agent_type
      d$cumulative_wins = as.numeric(0)
      for (i in 2:length(d$level)){
        if (d$level[i]>d$level[i-1]){
          d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
          # d$sparse_levels_won[i] = d$cumulative_wins[i]
        }
        else{
          d$cumulative_wins[i] = d$cumulative_wins[i-1]
        }
      }
      d$level_number = d$level
      
      rainbowdata = rbind(rainbowdata,d)
    }
    data = rainbowdata
    data$modelrun_ID = NA
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }else if (data_to_load == 'human'){
    humandata = list()
    for (humandatapath in humandatapaths){
      path = paste('~/Projects/atari/vgdl/humandata/',humandatapath, sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      if (length(humandata)==0){
        humandata = d
      }
      else{
        humandata = rbind(humandata,d)
      }
    }
    humandata$long_agent_type=as.factor('human')
    humandata$agent_type=as.factor('human')
    humandata$modelrun_ID = as.factor('oct29')
    humandata$condition = as.factor('full')
    
    humandata$game_name = as.factor(humandata$game_name)
    humandata = select(humandata, -levels_lost, -group, -gameNumber, -gameRound)
    data = humandata
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }
  
  data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
  beep(sound=2)
  return (data)
}

load_full_human_data = function(){
  fullhumandata = list()
  for (humandatapath in humandatapaths){
    path = paste('~/Projects/atari/vgdl/humandata/',humandatapath, sep='')
    d=read.csv(path, header=TRUE, na.strings='NA')
    if (length(fullhumandata)==0){
      fullhumandata = d
    }
    else{
      fullhumandata = rbind(fullhumandata,d)
    }
  }
  fullhumandata$long_agent_type=as.factor('human')
  fullhumandata$agent_type=as.factor('human')
  fullhumandata$modelrun_ID = as.factor('oct29')
  fullhumandata$condition = as.factor('full')
  
  fullhumandata$game_name = as.factor(fullhumandata$game_name)
  fullhumandata = select(fullhumandata, -levels_lost, -group, -gameNumber, -gameRound)
  data = fullhumandata
  data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
}

data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
return(data)
}

create_rand_string <- function() {
  a <- do.call(paste0, replicate(1, sample(LETTERS, 1, TRUE), FALSE))
  paste0(a, sprintf("%04d", sample(9999, 1, TRUE)), sample(LETTERS, 1, TRUE))
}



game_names = c(levels(data$game_name))
